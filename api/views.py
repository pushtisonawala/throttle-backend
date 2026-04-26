import redis
import json
import time
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from netguardian.settings import GEMINI_API_KEY, REDIS_HOST, REDIS_PORT
import logging

logger = logging.getLogger(__name__)

# Initialize Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class HealthCheckView(APIView):
    """Simple health check endpoint"""
    def get(self, request, *args, **kwargs):
        return Response({
            'status': 'healthy',
            'message': 'Throttle Backend API is running',
            'timestamp': time.time()
        }, status=status.HTTP_200_OK)

class ThrottleControlView(APIView):
    def post(self, request, *args, **kwargs):
        ip_address = request.data.get('ip')
        action = request.data.get('action')
        if not ip_address or not action or action not in ['throttle', 'unthrottle']:
            logger.error("Invalid throttle request: missing or invalid 'ip' or 'action'")
            return Response(
                {'error': "Missing or invalid 'ip' or 'action' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )
        command = {
            'ip': ip_address,
            'action': action,
        }
        if action == 'throttle':
            command['params'] = {'limit_mbps': 1}
        try:
            r.publish('throttle-commands', json.dumps(command))
            logger.debug(f"Published throttle command: {command}")
            return Response(
                {'status': 'command sent', 'command': command},
                status=status.HTTP_200_OK
            )
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            return Response(
                {'error': f'Could not connect to Redis: {e}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class DeviceStatsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            latest_stats = r.get('latest_network_stats')
            if not latest_stats:
                logger.warning("No network stats available in Redis")
                return Response({'error': 'No network stats available'}, status=status.HTTP_404_NOT_FOUND)
            stats = json.loads(latest_stats)
            logger.debug(f"Returning network stats: {stats}")
            return Response(stats, status=status.HTTP_200_OK)
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            return Response({'error': f'Could not connect to Redis: {e}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except json.JSONDecodeError:
            logger.error("Invalid network stats format in Redis")
            return Response({'error': 'Invalid network stats format'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateProfileView(APIView):
    SYSTEM_PROMPT = """
    You are a Network Configuration Expert assistant for a product called "throtl". Your sole purpose is to translate a user's answers from a multiple-choice questionnaire into a structured JSON configuration object.

    Analyze the user's JSON answers to determine the optimal values for THRESH_BYTES_PER_SEC, DEBOUNCE_SECS, and RATE.

    *Your Logic Guidelines:*
    -   *Environment is the baseline:* 'hostel' and 'cafe' settings should be much stricter (lower thresholds, faster debounce) than 'home' or 'power_user'.
    -   *Priority is the key modifier:* If the priority is 'video_calls' or 'gaming', the debounce must be very fast (3-5s) and the throttle aggressive to protect latency. If the priority is 'fast_downloads', the threshold can be higher and the debounce more tolerant.
    -   *Tolerance maps to debounce:* 'immediately' should result in a low DEBOUNCE_SECS (e.g., 3-4s). 'balanced' should be around 5-8s. 'tolerant' should result in a high DEBOUNCE_SECS (e.g., 15-20s).
    -   *Profile Name:* Create a short, creative profile_name that reflects the user's choices.

    You MUST respond with ONLY a valid JSON object and nothing else. No conversational text, explanations, or markdown formatting.
    """

    def post(self, request, *args, **kwargs):
        answers = request.data.get('answers')
        if not isinstance(answers, dict):
            logger.error("Invalid answers payload received")
            return Response({'error': 'Invalid "answers" payload.'}, status=status.HTTP_400_BAD_REQUEST)

        user_input_json = json.dumps(answers, indent=2)
        full_prompt = f"{self.SYSTEM_PROMPT}\n\nUSER'S ANSWERS (JSON INPUT):\n{user_input_json}\n\nYOUR JSON RESPONSE (JSON OUTPUT):"

        try:
            # Demo mode: Hardcoded response for reliability
            logger.info("DEMO MODE: Returning hardcoded LLM response for speed and reliability")
            time.sleep(1.5)  # Simulate API call
            llm_output_text = """
            {
              "profile_name": "Custom Profile (WFH Focus)",
              "THRESH_BYTES_PER_SEC": 250000,
              "DEBOUNCE_SECS": 4,
              "RATE": "1.5mbit"
            }
            """

            # Real LLM call (uncomment for production after demo)
            # model = genai.GenerativeModel('gemini-1.5-flash')
            # response = model.generate_content(full_prompt)
            # llm_output_text = response.text.strip()
            # if llm_output_text.startswith('```json'):
            #     llm_output_text = llm_output_text.split('```json')[1].rsplit('```', 1)[0].strip()

            config_data = json.loads(llm_output_text)
            logger.debug(f"Generated profile: {config_data}")
            return Response(config_data, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            logger.error("LLM returned invalid JSON")
            return Response({'error': 'LLM returned invalid JSON.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"LLM error: {e}")
            # Fallback for demo reliability
            fallback_config = {
                "profile_name": "Generated Demo Profile",
                "THRESH_BYTES_PER_SEC": 250000,
                "DEBOUNCE_SECS": 5,
                "RATE": "2mbit"
            }
            logger.info("Using fallback config due to LLM failure")
            return Response(fallback_config, status=status.HTTP_200_OK)
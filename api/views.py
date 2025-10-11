import redis
import json
import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from netguardian.settings import GEMINI_API_KEY

# Initialize Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

# Configure Gemini LLM
genai.configure(api_key=GEMINI_API_KEY)

class ThrottleControlView(APIView):
    def post(self, request, *args, **kwargs):
        ip_address = request.data.get('ip')
        action = request.data.get('action')
        if not ip_address or not action or action not in ['throttle', 'unthrottle']:
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
        except redis.exceptions.ConnectionError as e:
            return Response(
                {'error': f'Could not connect to Redis: {e}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response(
            {'status': 'command sent', 'command': command},
            status=status.HTTP_200_OK
        )

class DeviceStatsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            latest_stats = r.get('latest_network_stats')
            if not latest_stats:
                return Response({'error': 'No network stats available'}, status=status.HTTP_404_NOT_FOUND)
            stats = json.loads(latest_stats)
            # v2.0 format is already handled as JSON, no changes needed
            return Response(stats, status=status.HTTP_200_OK)
        except redis.exceptions.ConnectionError as e:
            return Response({'error': f'Could not connect to Redis: {e}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid network stats format'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateProfileView(APIView):
    SYSTEM_PROMPT = """
    You are a Network Configuration Expert assistant. Your sole purpose is to translate a user's answers from a multiple-choice questionnaire into a structured JSON configuration object for the NetGuardian system.

    You will receive a JSON object with the user's answers. Analyze the combination of answers to determine the optimal values for THRESH_BYTES_PER_SEC, DEBOUNCE_SECS, and RATE.

    *Your Logic Guidelines:*
    -   *Environment is the baseline:* 'hostel' and 'cafe' settings should be much stricter (lower thresholds, faster debounce) than 'home' or 'power_user'.
    -   *Priority is the key modifier:* If the priority is 'video_calls' or 'gaming', the debounce should be very fast and the throttle aggressive to protect latency. If the priority is 'fast_downloads', the threshold can be higher.
    -   *Tolerance maps to debounce:* 'immediately' should be a very low DEBOUNCE_SECS (e.g., 3-4s). 'only_if_huge_problem' should be a high DEBOUNCE_SECS (e.g., 15-20s).

    You MUST respond with ONLY a valid JSON object and nothing else. No conversational text, explanations, or markdown formatting.
    """

    def post(self, request, *args, **kwargs):
        answers = request.data.get('answers')
        if not answers or not isinstance(answers, dict):
            return Response({'error': 'Invalid "answers" payload'}, status=status.HTTP_400_BAD_REQUEST)

        # Construct prompt
        user_input_json = json.dumps(answers, indent=2)
        full_prompt = f"{self.SYSTEM_PROMPT}\n\nUSER'S ANSWERS (JSON INPUT):\n{user_input_json}\n\nYOUR JSON RESPONSE (JSON OUTPUT):"

        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(full_prompt)
            llm_output_text = response.text.strip()

            # Clean LLM output if needed (remove backticks or markdown)
            if llm_output_text.startswith('```json'):
                llm_output_text = llm_output_text.split('```json')[1].rsplit('```', 1)[0].strip()

            config_data = json.loads(llm_output_text)

            return Response(config_data, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({'error': 'LLM returned invalid JSON'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Fallback for demo
            fallback_config = {
                "profile_name": "Generated Demo Profile",
                "THRESH_BYTES_PER_SEC": 250000,
                "DEBOUNCE_SECS": 5,
                "RATE": "2mbit"
            }
            return Response(fallback_config, status=status.HTTP_200_OK)
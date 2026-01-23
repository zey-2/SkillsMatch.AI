"""Socket.IO event handlers for the web app."""

import json
import os
from datetime import datetime
from pathlib import Path
from functools import wraps

from flask import copy_current_request_context
from flask_socketio import emit

# Import centralized API key loader
try:
    from .config import get_openai_api_key
except ImportError:
    from config import get_openai_api_key


def register_socket_handlers(socketio, load_config) -> None:
    """Register Socket.IO handlers on the provided SocketIO instance."""

    @socketio.on("send_chat_message")
    def handle_chat_message(data):
        """Handle chat messages with AI career advisor."""
        try:
            message = data.get("message", "").strip()
            chat_history = data.get("chat_history", [])

            if not message:
                return

            print(f"🤖 DEBUG: Received chat message: {message}")
            emit("chat_response", {"type": "thinking", "message": "AI is thinking..."})

            # Wrap chat_task with copy_current_request_context to preserve Flask context
            @copy_current_request_context
            def chat_task():
                try:
                    config = load_config()

                    # Use centralized API key loader
                    openai_api_key = get_openai_api_key()
                    github_token = config.get("github_token") or os.environ.get(
                        "GITHUB_TOKEN"
                    )

                    if not openai_api_key and not github_token:
                        demo_responses = {
                            "hello": "👋 Hello! I'm your AI Career Advisor (Demo Mode). I can help with career guidance, skills development, and job market insights in Singapore!",
                            "career": "🚀 For career development in Singapore, I recommend exploring SkillsFuture courses and identifying in-demand skills like data analytics, digital marketing, and software development.",
                            "skills": "💡 Popular skills in Singapore's job market include: Python programming, data analysis, digital marketing, project management, and cloud computing. What area interests you?",
                            "tech": "💻 Tech careers in Singapore are booming! Consider roles in software development, data science, cybersecurity, or cloud architecture. The government supports tech skill development through various initiatives.",
                            "time": f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Singapore Time. How can I help with your career today?",
                            "default": "🤖 I'm running in demo mode. To unlock full AI capabilities, please set your GITHUB_TOKEN environment variable. Meanwhile, I can provide basic career guidance! Try asking about 'skills', 'tech careers', or 'singapore jobs'.",
                        }

                        message_lower = message.lower()
                        response = demo_responses["default"]

                        for keyword, demo_response in demo_responses.items():
                            if keyword in message_lower:
                                response = demo_response
                                break

                        response += (
                            "\n\n💡 **To enable full AI chat:** "
                            "Set GITHUB_TOKEN environment variable with your GitHub "
                            "Personal Access Token."
                        )

                        emit("chat_response", {"type": "ai", "message": response})
                        return

                    from openai import OpenAI

                    skills_context = ""
                    try:
                        skills_db_path = Path("../data/skills_database.json")
                        if skills_db_path.exists():
                            with open(skills_db_path, "r") as file_handle:
                                skills_data = json.load(file_handle)
                                sample_skills = list(skills_data.keys())[:20]
                                skills_context = (
                                    "Available skills in database: "
                                    f"{', '.join(sample_skills)}"
                                )
                    except Exception as error:
                        print(f"Could not load skills context: {error}")

                    messages = [
                        {
                            "role": "system",
                            "content": f"""You are an AI Career Advisor for SkillsMatch.AI, specializing in Singapore's job market and skills development.

Your expertise includes:
- Career guidance and planning in Singapore
- Skills development recommendations based on MySkillsFuture.gov.sg data
- Job market insights and trends
- Interview preparation and career transitions
- Professional development advice

{skills_context}

Guidelines:
- Provide practical, actionable advice
- Reference Singapore's job market and SkillsFuture initiatives when relevant
- Be encouraging and supportive
- Ask clarifying questions when needed
- Keep responses concise but comprehensive
- Use emojis occasionally to make conversations friendly

Current context: Singapore job market, SkillsFuture ecosystem, and career development.""",
                        }
                    ]

                    for hist_msg in chat_history[-10:]:
                        if hist_msg.get("sender") == "user":
                            messages.append(
                                {"role": "user", "content": hist_msg.get("message", "")}
                            )
                        elif hist_msg.get("sender") == "ai":
                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": hist_msg.get("message", ""),
                                }
                            )

                    messages.append({"role": "user", "content": message})

                    api_success = False
                    last_error = None

                    if openai_api_key and not api_success:
                        openai_models = [
                            "gpt-5-mini",
                            "gpt-4o-mini",
                        ]

                        for model_name in openai_models:
                            try:
                                print(
                                    "🤖 DEBUG: Trying OpenAI API with model: "
                                    f"{model_name}"
                                )
                                client = OpenAI(api_key=openai_api_key)

                                # gpt-5-mini uses max_completion_tokens, older models use max_tokens
                                completion_params = {
                                    "model": model_name,
                                    "messages": messages,
                                    "temperature": 0.7,
                                    "top_p": 0.95,
                                }

                                if model_name == "gpt-5-mini":
                                    completion_params["max_completion_tokens"] = 800
                                else:
                                    completion_params["max_tokens"] = 800

                                response = client.chat.completions.create(
                                    **completion_params
                                )

                                ai_message = response.choices[0].message.content
                                print(
                                    "🤖 DEBUG: OpenAI API succeeded with "
                                    f"{model_name} ({len(ai_message)} characters)"
                                )
                                emit(
                                    "chat_response",
                                    {"type": "ai", "message": ai_message},
                                )
                                api_success = True
                                break
                            except Exception as openai_error:
                                print(
                                    "🤖 DEBUG: OpenAI model "
                                    f"{model_name} failed: {openai_error}"
                                )
                                last_error = openai_error

                    if github_token and not api_success:
                        github_models = [
                            "gpt-5-mini",
                            "gpt-4o-mini",
                        ]

                        for model_name in github_models:
                            try:
                                print(
                                    "🤖 DEBUG: Trying GitHub models API with: "
                                    f"{model_name}"
                                )
                                client = OpenAI(
                                    base_url="https://models.inference.ai.azure.com",
                                    api_key=github_token,
                                )
                                response = client.chat.completions.create(
                                    model=model_name,
                                    messages=messages,
                                    temperature=0.7,
                                    max_tokens=800,
                                    top_p=0.95,
                                )

                                ai_message = response.choices[0].message.content
                                print(
                                    "🤖 DEBUG: GitHub API succeeded with "
                                    f"{model_name} ({len(ai_message)} characters)"
                                )
                                emit(
                                    "chat_response",
                                    {"type": "ai", "message": ai_message},
                                )
                                api_success = True
                                break
                            except Exception as github_error:
                                print(
                                    "🤖 DEBUG: GitHub model "
                                    f"{model_name} failed: {github_error}"
                                )
                                last_error = github_error

                    if not api_success:
                        if last_error:
                            raise last_error
                        raise Exception("No working API available")

                except Exception as error:
                    print(f"🤖 DEBUG: Chat error: {str(error)}")
                    import traceback

                    traceback.print_exc()

                    error_msg = f"❌ Sorry, I encountered an error: {str(error)}"
                    if (
                        ("403" in str(error) and "no_access" in str(error))
                        or ("429" in str(error) and "insufficient_quota" in str(error))
                        or "quota" in str(error).lower()
                    ):
                        print(
                            "🤖 DEBUG: Model access/quota issue, falling back to enhanced demo mode"
                        )

                        demo_responses = {
                            "time": f"🕐 The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Singapore Time.",
                            "career": "🚀 **Career Development in Singapore:**\n\n• **Tech Sector**: High demand for software developers, data scientists, and cybersecurity experts\n• **Healthcare**: Growing opportunities in digital health and eldercare\n• **Finance**: FinTech and digital banking are expanding rapidly\n• **Logistics**: Smart port technologies and supply chain optimization\n\n💡 Consider exploring SkillsFuture courses to upskill in these areas!",
                            "skills": "💼 **In-Demand Skills in Singapore 2025:**\n\n**Technical Skills:**\n• Python, JavaScript, SQL programming\n• Data analysis and visualization\n• Cloud computing (AWS, Azure)\n• Cybersecurity fundamentals\n\n**Soft Skills:**\n• Digital marketing and e-commerce\n• Project management (Agile/Scrum)\n• Cross-cultural communication\n• Problem-solving and critical thinking",
                            "default": f"🤖 **Smart Career Guidance** (Enhanced Mode)\n\nI can help you with career questions about Singapore's job market! While I don't have full AI access right now, I can provide valuable insights about:\n\n• Tech career pathways\n• In-demand skills\n• SkillsFuture opportunities\n• Industry trends\n\n**Your question:** \"{message}\"\n\nFor this query, I'd recommend researching current market trends and considering upskilling through official Singapore resources like SkillsFuture.gov.sg and MyCareersFuture.gov.sg.",
                        }

                        message_lower = message.lower()
                        response = demo_responses["default"]

                        if any(
                            word in message_lower
                            for word in ["time", "what time", "current time"]
                        ):
                            response = demo_responses["time"]
                        elif any(
                            word in message_lower
                            for word in ["career", "job", "work", "profession"]
                        ):
                            response = demo_responses["career"]
                        elif any(
                            word in message_lower
                            for word in ["skill", "learn", "study", "course"]
                        ):
                            response = demo_responses["skills"]

                        response += "\n\n⚠️ **Note:** Running in enhanced demo mode due to AI model access limitations."

                        emit("chat_response", {"type": "ai", "message": response})
                        return

                    if "401" in str(error):
                        error_msg = (
                            "🔑 Authentication failed. Please check your GitHub token."
                        )
                    elif (
                        "429" in str(error)
                        or "rate limit" in str(error).lower()
                        or "quota" in str(error).lower()
                    ):
                        error_msg = (
                            "💳 OpenAI quota exceeded. Using fallback demo mode above."
                        )
                    elif (
                        "network" in str(error).lower()
                        or "connection" in str(error).lower()
                    ):
                        error_msg = "🌐 Network issue. Please check your connection and try again."

                    emit("chat_response", {"type": "error", "message": error_msg})

            socketio.start_background_task(chat_task)

        except Exception as error:
            print(f"🤖 DEBUG: Chat handler error: {str(error)}")
            emit(
                "chat_response",
                {"type": "error", "message": f"Error processing message: {str(error)}"},
            )

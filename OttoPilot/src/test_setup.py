def test():
    try:
        from config import settings
        print(f"✅ Config loaded!")
        print(f"✅ API Key: {settings.google_api_key[:10]}...")

        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=settings.google_api_key
        )
        response = llm.invoke("Say 'Hello'")
        print(f"✅ Gemini works! Response: {response.content}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test()
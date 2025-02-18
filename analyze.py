import requests
import discord
import openai
import time
import os  # ✅ Use environment variables instead of config.py


user_request_log = {}  # Store user requests {user_id: timestamp}


async def fetch_crypto_data(token):
    """Fetch crypto data by dynamically finding the correct CoinGecko ID"""

    # Step 1: Get the correct ID from CoinGecko
    search_url = f"https://api.coingecko.com/api/v3/search?query={token.lower()}"
    search_response = requests.get(search_url)

    if search_response.status_code == 200:
        results = search_response.json().get("coins", [])
        if results:
            correct_id = results[0]["id"]  # Use the first matching result
        else:
            return None  # No match found
    else:
        return None  # API error

    # Step 2: Fetch full data using the correct ID
    coin_url = f"https://api.coingecko.com/api/v3/coins/{correct_id}"
    coin_response = requests.get(coin_url)

    if coin_response.status_code == 200:
        return coin_response.json()  # Return the correct coin data
    else:
        return None  # Coin still not found


async def analyze_with_chatgpt(data, token):
    """Use ChatGPT API to analyze a crypto coin using our ranking system and only display the final analysis"""

    openai_api_key = os.getenv("OPENAI_API_KEY")  # ✅ Get API key from Render's environment variables

    if not openai_api_key:
        raise ValueError("🚨 OPENAI_API_KEY is not set in the environment variables!")

    client = openai.OpenAI(api_key=openai_api_key)

    # Extract only necessary fields
    filtered_data = {
        "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd", "N/A"),
        "total_volume": data.get("market_data", {}).get("total_volume", {}).get("usd", "N/A"),
        "market_cap_rank": data.get("market_data", {}).get("market_cap_rank", "N/A"),
        "circulating_supply": data.get("market_data", {}).get("circulating_supply", "N/A"),
        "max_supply": data.get("market_data", {}).get("max_supply", "N/A"),
        "community_followers": data.get("community_data", {}).get("twitter_followers", 0),
        "developer_activity": data.get("developer_data", {}).get("commit_count_4_weeks", 0),
        "categories": data.get("categories", [])
    }

    # Detect meme coins and reject them
    meme_keywords = ["Meme", "Dogecoin", "Shiba", "Pepe", "Floki", "Bonk"]
    if any(keyword.lower() in str(filtered_data["categories"]).lower() for keyword in meme_keywords):
        return "🚨 **This coin is classified as a meme coin with no real utility and will not be analyzed.**"

    prompt = f"""
    You are a crypto analyst using a structured **12-factor** evaluation model for rating cryptocurrencies.

    **Scoring Rules:**
    - **Each factor is scored out of 10.**
    - **Multiply each factor's score by 8.33 to scale correctly to 1000 points.**
    - **Ensure the total score sums correctly to a 1000-point scale.**
    
    **Evaluation Categories (Each Max 10 Points):**
    - **Tokenomics**
    - **Adoption & Network Effects**
    - **Narrative & Hype Cycle**
    - **Interoperability**
    - **Technology & Infrastructure**
    - **Market Liquidity & Volume**
    - **Partnerships & Institutional Interest**
    - **Developer Ecosystem**
    - **Security & Decentralization**
    - **Community Strength**
    - **Roadmap & Development**
    - **Utility & Use Case**

    **Here is the real data for {token.upper()}:**
    {filtered_data}

    **Instructions:**
    - Assign a score (0-10) for each factor.
    - **Multiply each score by 8.33 to get the actual contribution to the final score.**
    - **Ensure the sum of all scores is correctly calculated.**
    - **ONLY DISPLAY the final structured analysis. Do NOT show how the score was calculated.**
    - **Sum up all scores to get a final total score (out of 1000).**
    - Assign a **Risk Level** based on:
      - **800+ = Low Risk**
      - **500-799 = Medium Risk**
      - **Below 500 = High Risk**
    - **Ensure the scores follow this exact format:**
    
    ```
    🔍 {token.upper()} Analysis
    📊 Total Score: XXX / 1000
    📉 Risk Level: Low/Medium/High

    💰 Tokenomics (XX%) → [Brief explanation]
    🌍 Adoption & Network Effects (XX%) → [Brief explanation]
    🚀 Narrative & Hype Cycle (XX%) → [Brief explanation]
    🔗 Interoperability (XX%) → [Brief explanation]
    ⚡ Technology & Infrastructure (XX%) → [Brief explanation]
    📈 Market Liquidity & Volume (XX%) → [Brief explanation]
    🏦 Partnerships & Institutions (XX%) → [Brief explanation]
    💻 Developer Ecosystem (XX%) → [Brief explanation]
    🛡️ Security & Decentralization (XX%) → [Brief explanation]
    👥 Community Strength (XX%) → [Brief explanation]
    📅 Roadmap & Development (XX%) → [Brief explanation]
    🔧 Utility & Use Case (XX%) → [Brief explanation]

    Market Cap: ${filtered_data["market_cap"]}
    24H Volume: ${filtered_data["total_volume"]}
    Market Cap Rank: {filtered_data["market_cap_rank"]}
    ```

    **Important:**
    - **DO NOT include a separate breakdown of calculations.**
    - **DO NOT display the step-by-step multiplication process.**
    - **Ensure all calculations are correct before responding.**
    - **Factor percentages should never exceed 100%.**
    """

    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            temperature=0,
            messages=[{"role": "system", "content": "You are an expert crypto analyst."},
                      {"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content  # Return only the final structured AI response

    except openai.OpenAIError as e:
        return f"🚨 OpenAI API error: {e}"

async def can_request_analysis(user_id):
    """Check if the user has already made a request today"""
    if user_id in user_request_log:
        last_request_time = user_request_log[user_id]
        if time.time() - last_request_time < 86400:  # 86400 seconds = 24 hours
            return False  # User must wait
    return True  # User can request

async def get_crypto_analysis(interaction, token):
    """Fetch data and send it to ChatGPT API for analysis, limiting requests per user"""

    user_id = interaction.user.id  # Get Discord User ID

    # ✅ Check if the user has already made a request today
    if not await can_request_analysis(user_id):
        await interaction.response.send_message(
            f"🚨 You can only request one analysis per day. Try again later!", ephemeral=True
        )
        return

    await interaction.response.defer()

    data = await fetch_crypto_data(token)
    if not data:
        await interaction.followup.send(embed=discord.Embed(title=f"❌ {token.upper()} Not Found", color=0xFF0000))
        return

    analysis = await analyze_with_chatgpt(data, token)

    MAX_EMBED_LENGTH = 4096
    if len(analysis) > MAX_EMBED_LENGTH:
        analysis = analysis[:MAX_EMBED_LENGTH - 10] + "...\n(Analysis truncated)"

    embed = discord.Embed(title=f"🔍 {token.upper()} Analysis", color=0x00ff00)
    embed.description = analysis

    # ✅ Store the user's request timestamp
    user_request_log[user_id] = time.time()

    await interaction.followup.send(embed=embed)

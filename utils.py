# Points multiplier to scale to 1000
POINT_MULTIPLIER = 21.27

# Define max possible points per factor
FACTOR_WEIGHTS = {
    "Tokenomics": 5,
    "Adoption & Network Effects": 5,
    "Narrative & Hype Cycle": 5,
    "Interoperability": 5,
    "Technology & Infrastructure": 4,
    "Market Liquidity & Volume": 4,
    "Partnerships & Institutions": 4,
    "Developer Ecosystem": 4,
    "Security & Decentralization": 3,
    "Community Strength": 3,
    "Roadmap & Development": 3,
    "Utility & Use Case": 2,
}

def calculate_score(data):
    """Calculates the total crypto score based on 12 ranking factors"""
    total_score = 0
    category_scores = {}

    # **Evaluate each factor and assign a rating**
    for category, max_points in FACTOR_WEIGHTS.items():
        earned_points, explanation = evaluate_factor(category, data, max_points)
        scaled_score = earned_points * POINT_MULTIPLIER
        total_score += scaled_score
        category_scores[category] = (earned_points, max_points, explanation)

    return round(total_score, 1), category_scores  # ✅ Properly rounds total score

def evaluate_factor(category, data, max_points):
    """Assigns a score for each factor based on real data and returns a brief explanation"""

    # **Tokenomics (5)**
    if category == "Tokenomics":
        supply = data.get('market_data', {}).get('max_supply', None)
        circulating = data.get('market_data', {}).get('circulating_supply', None)

        if supply and circulating:
            supply_ratio = circulating / supply
            if supply_ratio < 0.5:
                return max_points, "Low inflation risk, good scarcity."
            else:
                return max_points - 1, "High supply, inflationary risk."
        elif circulating and not supply:  # If max supply is missing
            return max_points - 2, "No fixed supply, potential inflation risk."
        return 0, "No supply data available."

    # **Adoption & Network Effects (5)**
    elif category == "Adoption & Network Effects":
        active_users = data.get('community_data', {}).get('twitter_followers', 0)
        if active_users > 500000:
            return max_points, "Strong adoption, large active user base."
        elif active_users > 100000:
            return max_points - 1, "Moderate adoption, growing interest."
        return max_points - 2, "Weak adoption, low active users."

    # **Narrative & Hype (5)**
    elif category == "Narrative & Hype Cycle":
        market_rank = data.get('market_data', {}).get('market_cap_rank', 1000)
        if market_rank < 50:
            return max_points, "Strong hype and trending narrative."
        elif market_rank < 200:
            return max_points - 1, "Moderate hype, some market relevance."
        return max_points - 2, "Low hype, struggling to gain traction."

    # **Technology & Infrastructure (4)**
    elif category == "Technology & Infrastructure":
        dev_activity = data.get('developer_data', {}).get('commit_count_4_weeks', 0)
        if dev_activity > 50:
            return max_points, "Strong development, frequent updates."
        elif dev_activity > 10:
            return max_points - 1, "Moderate development activity."
        return max_points - 2, "Low developer engagement, slow progress."

    # **Market Liquidity & Volume (4)**
    elif category == "Market Liquidity & Volume":
        volume = data.get('market_data', {}).get('total_volume', {}).get('usd', 0)
        if volume > 100000000:
            return max_points, "Highly liquid, easy to trade."
        elif volume > 1000000:
            return max_points - 1, "Moderate liquidity, manageable trading."
        return max_points - 2, "Low liquidity, difficult to buy/sell."

    # **Partnerships & Institutions (4)**
    elif category == "Partnerships & Institutions":
        if "Institutional" in data.get('categories', []):
            return max_points, "Backed by institutions, strong credibility."
        return max_points - 1, "Limited institutional backing."

    # **Developer Ecosystem (4)**
    elif category == "Developer Ecosystem":
        forks = data.get('developer_data', {}).get('forks', 0)
        if forks > 100:
            return max_points, "Highly active developer community."
        return max_points - 1, "Moderate developer engagement."

    # **Security & Decentralization (3)**
    elif category == "Security & Decentralization":
        decentralization_score = data.get('developer_data', {}).get('forks', 0)
        if decentralization_score > 100:
            return max_points, "Highly decentralized and secure."
        return max_points - 1, "Moderate security, potential vulnerabilities."

    # **Community Strength (3)**
    elif category == "Community Strength":
        followers = data.get('community_data', {}).get('twitter_followers', 0)
        if followers > 1000000:
            return max_points, "Extremely strong community presence."
        elif followers > 500000:
            return max_points - 1, "Very strong community presence."
        elif followers > 100000:
            return max_points - 2, "Moderate community engagement."
        return max_points - 3, "Weak community presence, needs more growth."

    # **Roadmap & Development (3)**
    elif category == "Roadmap & Development":
        return max_points, "Consistent updates and progress."

    # **Utility & Use Case (2)**
    elif category == "Utility & Use Case":
        if "DeFi" in data.get('categories', []):
            return max_points, "Real-world DeFi application."
        return max_points - 1, "Limited practical utility."

    return 0, "Insufficient data for evaluation."

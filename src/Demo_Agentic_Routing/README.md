# Demo_Agentic_Routing

A CrewAI-powered customer service demo that demonstrates intelligent emotion-based routing and escalation using AI agents. This demo showcases how multiple AI agents can work together to analyze customer sentiment, provide appropriate responses, and automatically escalate cases that require manager intervention.

## 🎯 What This Demo Does

This demo simulates a customer service workflow where AI agents collaborate to:

1. **Analyze Customer Sentiment** - Detect emotions like anger, frustration, happiness, or neutrality in customer messages
2. **Provide Intelligent Responses** - Generate appropriate customer service responses based on detected sentiment
3. **Make Escalation Decisions** - Automatically escalate angry or highly frustrated customers to managers
4. **Quality Assurance** - Monitor and review the entire interaction process

The demo processes 4 different customer scenarios and shows how the system handles each case, including automatic escalation for angry customers.

## 🏗️ Architecture

The demo uses **CrewAI** to orchestrate three specialized AI agents:

- **Customer Service Agent** - Handles customer interactions and provides responses
- **Escalation Specialist** - Analyzes sentiment and decides when escalation is needed
- **Quality Assurance Supervisor** - Monitors interaction quality and processes

Each agent has specific tools and responsibilities, working together in a sequential workflow to process customer interactions.

## 🚀 Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- **Emotion API service running** (from the main project)

### Installation

1. **Start the emotion service first:**
   ```bash
   cd src
   # For Mac (ARM64):
   IMAGE_TAG=arm64 docker-compose up --build -d
   # For Mac (Intel):
   IMAGE_TAG=mac_amd64 docker-compose up --build -d
   # For RPi (ARM):
   IMAGE_TAG=arm docker-compose up --build -d
   # For Intel machine (AMD64):
   IMAGE_TAG=amd64 docker-compose up --build -d
   ```

2. **Navigate to the demo directory:**
   ```bash
   cd Demo_Agentic_Routing
   ```

3. **Install required dependencies:**
   ```bash
   pip install crewai langchain-openai pydantic requests
   ```

   **Note:** The demo will work without CrewAI dependencies for demonstration purposes, but you'll see a note about missing packages.

4. **Optional: Set up OpenAI API (for full functionality):**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

## 🎮 Running the Demo

### Quick Start

1. **Test the emotion API first (optional):**
   ```bash
   python test_api.py
   ```

2. **Run the demo script:**
   ```bash
   python demo.py
   ```

### What Happens When You Run It

The demo will process 4 customer interactions:

1. **CUST001** - Neutral inquiry about order status
2. **CUST002** - Angry customer with strong negative sentiment
3. **CUST003** - Frustrated customer with subscription issues
4. **CUST004** - Happy customer expressing satisfaction

For each interaction, you'll see:
- Sentiment analysis results
- Customer service response
- Escalation decision
- Quality assurance review

## 📊 Expected Output

After running the demo, you'll see a comprehensive summary like this:

```
📊 EMOTION-BASED ESCALATION SUMMARY
============================================================
Total Interactions: 4
Escalations: 2
Escalation Rate: 50.0%

🎯 Emotion Detection Results:
- Customer CUST001: frustrated (100.0%) → ✅ Handled
- Customer CUST002: angry (100.0%) → ⚠️ ESCALATED
- Customer CUST003: angry (100.0%) → ⚠️ ESCALATED
- Customer CUST004: happy (100.0%) → ✅ Handled

🚨 Escalated Cases:
- Customer CUST002 (angry): Successfully escalated to Manager MGR469. Ticket: ESC-CUST002-5037
- Customer CUST003 (angry): Successfully escalated to Manager MGR448. Ticket: ESC-CUST003-5119

✅ Demo completed! Your emotion API integration is working!
💡 The system automatically escalates based on:
   • anger 😡 & disgust 🤢 → Immediate escalation
   • sadness 😢, fear 😨, confusion 😕 → Escalate if high confidence
   • sarcasm 🤨 → Escalate if moderate confidence
   • happiness 😊, love ❤️, surprise 😲 → No escalation needed
```

## 🔧 How It Works

### Sentiment Analysis

The demo integrates with the main emotion API service to perform real emotion detection:
- **Primary**: Uses the emotion API at `http://localhost:8000/predict` for accurate emotion detection
- **Fallback**: If the API is unavailable, falls back to keyword-based sentiment analysis
- **Emotion Mapping**: Maps API emotions to customer service categories:
  - `anger`, `disgust` → ANGRY (immediate escalation)
  - `sadness`, `fear`, `confusion` → FRUSTRATED (escalate if high confidence)
  - `happiness`, `love`, `surprise` → HAPPY (no escalation needed)
  - `neutral` or other → NEUTRAL (normal handling)

### Escalation Logic

The system escalates customers based on:
- **Immediate escalation**: Anger or disgust emotions from the API (high confidence)
- **Conditional escalation**: Sadness, fear, or confusion emotions (if high confidence)
- **Normal handling**: Happiness, love, surprise, or neutral emotions
- **Mock API integration**: Simulates real escalation API calls for demonstration

### Agent Workflow

1. **Sentiment Analysis** - Escalation Agent analyzes the customer message
2. **Response Generation** - Customer Service Agent crafts appropriate response
3. **Escalation Decision** - Escalation Agent decides if manager intervention is needed
4. **Quality Review** - QA Agent reviews the entire interaction

## 🛠️ Customization

### Adding New Test Cases

You can modify the `test_interactions` list in the `main()` function to add new customer scenarios:

```python
CustomerInteraction(
    customer_id="CUST005",
    message="Your new test message here",
    sentiment=CustomerSentiment.NEUTRAL  # or ANGRY, FRUSTRATED, HAPPY
)
```

### Modifying Escalation Rules

Edit the escalation logic in the `simulate_workflow()` method to change when customers get escalated:

```python
if sentiment_result["sentiment"] == "angry" or sentiment_result["anger_indicators"] >= 2:
    # Escalation logic here
```

### Adding New Sentiment Keywords

Update the keyword lists in the `SentimentAnalysisTool` class:

```python
anger_keywords = ["angry", "furious", "mad", "your_new_keyword"]
frustration_keywords = ["annoyed", "disappointed", "your_new_keyword"]
positive_keywords = ["happy", "great", "your_new_keyword"]
```

## 🔗 Integration with Emotion Service

This demo is fully integrated with the main emotion service stack:

1. **Real Emotion API Integration** - Uses the actual emotion API for sentiment analysis
2. **Automatic Fallback** - Falls back to keyword analysis if the API is unavailable
3. **API Health Checking** - Verifies the emotion service is running before starting
4. **Configurable Endpoints** - Easy to modify API URLs for different environments

### API Requirements

- **Emotion API**: Must be running on `http://localhost:8000/predict`
- **Expected Response Format**: `{"emotion": "emotion_name", "confidence": 0.0-1.0}`
- **Timeout**: 10 seconds for API calls
- **Fallback**: Automatic fallback to keyword-based analysis if API fails

## 📝 Key Features

- **Multi-Agent Architecture** - Uses CrewAI for agent orchestration
- **Real Emotion API Integration** - Uses the actual emotion service for sentiment analysis
- **Intelligent Escalation** - Automatic escalation based on real emotion detection
- **Robust Fallback System** - Falls back to keyword analysis if API is unavailable
- **API Health Monitoring** - Checks emotion service availability before starting
- **Comprehensive Logging** - Detailed output showing agent decision-making
- **Easy Customization** - Simple to modify test cases and rules
- **Educational Value** - Great for learning about AI agent collaboration

## 🐛 Troubleshooting

### Common Issues

1. **Emotion API Not Running**: 
   - Make sure the emotion service is started: `cd src && IMAGE_TAG=amd64 docker-compose up --build -d`
   - Check that the API is accessible: `curl http://localhost:8000/health`
   - The demo will fall back to keyword analysis if the API is unavailable

2. **Import Errors**: Make sure you've installed the required dependencies:
   ```bash
   pip install crewai langchain-openai pydantic requests
   ```

3. **Missing OpenAI Key**: The demo works without it, but you'll see a note about missing packages.

4. **Python Version**: Ensure you're using Python 3.8 or higher.

5. **API Connection Timeout**: If the emotion API is slow to respond, the demo will timeout after 10 seconds and use fallback analysis.

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed
2. Verify your Python version
3. Review the error messages in the console output

## 🎓 Learning Objectives

This demo helps you understand:
- How AI agents can collaborate on complex tasks
- Sentiment analysis and emotion detection
- Automated escalation workflows
- Customer service automation
- CrewAI framework usage
- API integration patterns

## 📚 Related Projects

This demo is part of the larger emotion-server-demo project. Check out:
- **Main Project**: [README.md](../../README.md)
- **Demo_Firehose**: [Social Media Sentiment Monitor](../Demo_Firehose/README.md)
- **Business Case**: [Business_Case.md](../../Business_Case.md)

---

**Note**: This demo is for educational and experimental purposes. It demonstrates AI agent collaboration and sentiment-based routing concepts but is not intended for production use without further development and security considerations.

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

### Installation

1. **Navigate to the demo directory:**
   ```bash
   cd src/Demo_Agentic_Routing
   ```

2. **Install required dependencies:**
   ```bash
   pip install crewai langchain-openai pydantic
   ```

   **Note:** The demo will work without these dependencies for demonstration purposes, but you'll see a note about missing packages.

3. **Optional: Set up OpenAI API (for full functionality):**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

## 🎮 Running the Demo

### Quick Start

Simply run the demo script:

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
Escalations: 1
Escalation Rate: 25.0%

🎯 Emotion Detection Results:
- Customer CUST001: neutral (50.0%) → ✅ Handled
- Customer CUST002: angry (90.0%) → ⚠️ ESCALATED
- Customer CUST003: frustrated (80.0%) → ✅ Handled
- Customer CUST004: happy (90.0%) → ✅ Handled

🚨 Escalated Cases:
- Customer CUST002 (angry): Successfully escalated to Manager MGR155. Ticket: ESC-CUST002-3677

✅ Demo completed! Your emotion API integration is working!
💡 The system automatically escalates based on:
   • anger 😡 & disgust 🤢 → Immediate escalation
   • sadness 😢, fear 😨, confusion 😕 → Escalate if high confidence
   • sarcasm 🤨 → Escalate if moderate confidence
   • happiness 😊, love ❤️, surprise 😲 → No escalation needed
```

## 🔧 How It Works

### Sentiment Analysis

The demo uses a keyword-based sentiment analysis system that detects:
- **Anger indicators**: "angry", "furious", "mad", "hate", "terrible", etc.
- **Frustration indicators**: "annoyed", "disappointed", "confused", "problem", etc.
- **Positive indicators**: "happy", "great", "excellent", "love", "thank you", etc.

### Escalation Logic

The system escalates customers based on:
- **Immediate escalation**: High anger indicators (2+ anger keywords)
- **Normal handling**: Neutral, positive, or low frustration cases
- **Mock API integration**: Simulates real escalation API calls

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

This demo is designed to work with the main emotion service stack. While it currently uses a mock sentiment analysis system, it can be easily integrated with the actual emotion API:

1. **Replace the mock sentiment analysis** with calls to the emotion API
2. **Use real escalation APIs** instead of the simulated ones
3. **Integrate with your customer service platform**

## 📝 Key Features

- **Multi-Agent Architecture** - Uses CrewAI for agent orchestration
- **Intelligent Escalation** - Automatic escalation based on sentiment analysis
- **Mock API Integration** - Simulates real-world API calls
- **Comprehensive Logging** - Detailed output showing agent decision-making
- **Easy Customization** - Simple to modify test cases and rules
- **Educational Value** - Great for learning about AI agent collaboration

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've installed the required dependencies:
   ```bash
   pip install crewai langchain-openai pydantic
   ```

2. **Missing OpenAI Key**: The demo works without it, but you'll see a note about missing packages.

3. **Python Version**: Ensure you're using Python 3.8 or higher.

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

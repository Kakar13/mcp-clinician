# Dynamic MCP Clinical Decision Support System

A sophisticated clinical decision support system that leverages **Model Context Protocol (MCP)** for intelligent, context-aware medical analysis and recommendations.

## 🔬 What is MCP (Model Context Protocol)?

The **Model Context Protocol (MCP)** is a crucial component of this system that maintains conversational context, system state, and interaction history across multiple exchanges. Our implementation provides:

- **Persistent Context Management**: Maintains conversation history and system state
- **Tool Registration**: Tracks active medical analysis tools and their usage
- **Context Windowing**: Provides relevant historical context to improve response quality
- **State Persistence**: Ability to save and restore context across sessions
- **Metadata Tracking**: Records detailed information about each interaction

### MCP Architecture in This System

```
┌─────────────────────────────────────────┐
│           MCP Context Manager           │
├─────────────────────────────────────────┤
│  • Conversation History                 │
│  • System State Tracking                │
│  • Active Tools Registry                │
│  • Metadata & Timestamps                │
│  • Context Windowing                    │
│  • Persistence Layer                    │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│      Clinical Decision Support          │
├─────────────────────────────────────────┤
│  • Symptom Analysis                     │
│  • Differential Diagnosis               │
│  • Treatment Guidelines                 │
│  • Claude AI Integration                │
└─────────────────────────────────────────┘
```

## 🚀 Features

### Core Medical Features
- **Intelligent Symptom Analysis**: Advanced normalization of patient-described symptoms
- **Differential Diagnosis**: AI-powered condition assessment based on symptom patterns
- **Treatment Guidelines**: Evidence-based treatment recommendations
- **Risk Assessment**: Urgency level determination and red flag identification

### MCP-Enhanced Features
- **Context-Aware Responses**: Each interaction builds upon previous conversations
- **Persistent Medical History**: Maintains patient interaction context across sessions
- **Intelligent Follow-ups**: Uses conversation history for more accurate assessments
- **Tool Usage Tracking**: Monitors which medical analysis tools are actively being used

## 📋 Prerequisites

- Python 3.8 or higher
- Anthropic API key (for Claude AI integration)
- pip (Python package installer)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Dynamic-MCP-Clinical-Decision-Support-System
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -e .
```

This will automatically install all required dependencies including:
- `anthropic` - Claude AI API client
- `mcp` - Model Context Protocol framework
- `httpx` - Async HTTP client
- `python-dotenv` - Environment variable management
- And other supporting libraries

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

To get an Anthropic API key:
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Generate an API key
4. Add it to your `.env` file

## 🏃‍♂️ Running the Application

### Method 1: Using the Console Command (Recommended)
After installation, you can run the app using the installed console script:
```bash
clinical-assistant
```

### Method 2: Using Python Module
```bash
python -m client.clinical_assistant
```

### Method 3: Direct Python Execution
```bash
python client/clinical_assistant.py
```

## 💻 Usage Example

```bash
🏥 Clinical Decision Support System
==================================================
Please describe your symptoms in detail (e.g., 'I have been feeling tired with a fever and cough')
Enter your symptoms: I've been having a persistent cough with fever and fatigue for the past 3 days

--------------------------------------------------
Analyzing symptoms: I've been having a persistent cough with fever and fatigue for the past 3 days
--------------------------------------------------
📊 ANALYSIS SUMMARY:
Original symptoms: I've been having a persistent cough with fever and fatigue for the past 3 days
Normalized symptoms: ['fever', 'cough', 'fatigue']
Potential conditions: ['Influenza', 'COVID-19', 'Pneumonia', 'Bronchitis']
Urgency level: moderate

🩺 CLINICAL RECOMMENDATIONS:
[Detailed AI-generated medical recommendations...]
```

## 🏗️ System Architecture

### Project Structure
```
Dynamic-MCP-Clinical-Decision-Support-System/
├── client/
│   ├── __init__.py
│   └── clinical_assistant.py      # Main application logic
├── servers/
│   ├── knowledge_server/
│   │   └── server.py             # Medical knowledge APIs
│   ├── guidelines_server/
│   │   └── server.py             # Treatment guidelines
│   └── symptom_server/
│       └── symptom.py            # Symptom analysis
├── utils/
│   ├── __init__.py
│   └── mcp_context.py            # MCP Context Manager
├── data/                         # Data storage
├── requirements.txt              # Dependencies
├── setup.py                      # Package configuration
└── README.md                     # This file
```

### MCP Context Manager Implementation

The `MCPContextManager` class provides:

```python
class MCPContextManager:
    def __init__(self):
        # Initialize context storage
        
    def add_conversation_turn(self, role, content, metadata=None):
        # Track each interaction
        
    def update_system_state(self, key, value):
        # Maintain system state
        
    def get_context_window(self, window_size=10):
        # Retrieve recent context
        
    def save_context(self, filepath):
        # Persist context to disk
```

## 🔧 Technical Details

### MCP Context Flow
1. **User Input**: Symptom description is logged to conversation history
2. **System Processing**: Each analysis step updates the system state
3. **Context Enhancement**: Historical context is retrieved for AI prompting
4. **Response Generation**: Claude receives both current analysis and context
5. **Context Update**: AI response is logged back to conversation history

### Medical Knowledge Integration
- **FDA API**: Drug information and contraindications
- **RxNorm**: Medication standardization
- **MedlinePlus**: Condition information
- **Local Knowledge Base**: Symptom mapping and treatment guidelines

### AI Integration
- **Model**: Claude Sonnet 4 (Anthropic)
- **Context-Aware Prompting**: Uses MCP context for enhanced responses
- **Medical Disclaimers**: Automatic inclusion of appropriate warnings
- **Educational Focus**: Emphasizes informational rather than diagnostic content

## ⚠️ Important Medical Disclaimers

- **This system is for educational purposes only**
- **Not a substitute for professional medical advice**
- **Always consult healthcare providers for medical concerns**
- **Emergency symptoms require immediate medical attention**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔮 Future Enhancements

- **Multi-Patient Context**: Support for multiple patient contexts
- **Enhanced MCP Features**: Advanced context search and retrieval
- **Integration APIs**: REST API for external system integration
- **Mobile Interface**: React Native or Flutter mobile app
- **Database Backend**: PostgreSQL or MongoDB for production deployment
- **Advanced Analytics**: Patient outcome tracking and analysis

## 🆘 Troubleshooting

### Common Issues

**ImportError: No module named 'utils.mcp_context'**
- Solution: Run `pip install -e .` to install the package properly

**ModuleNotFoundError: No module named 'anthropic'**
- Solution: Ensure all dependencies are installed with `pip install -r requirements.txt`

**API Key Not Found**
- Solution: Create a `.env` file with your `ANTHROPIC_API_KEY`

### Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify your API key is correctly configured
4. Check the console output for detailed error messages
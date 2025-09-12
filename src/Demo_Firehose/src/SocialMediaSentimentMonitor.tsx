import { useState, useEffect, useRef } from 'react';

// Define types
type Emotion = 'anger' | 'confusion' | 'desire' | 'disgust' | 'fear' | 'guilt' | 'happiness' | 'love' | 'neutral' | 'sadness' | 'sarcasm' | 'shame' | 'surprise';
type SentimentCategory = 'positive' | 'neutral' | 'negative';

interface Message {
  id: string;
  text: string;
  emotion: Emotion;
  emoji: string;
  confidence: number;
  sentimentValue: number;
  sentimentCategory: SentimentCategory;
  timestamp: Date;
}

// Map emotions to emojis, sentiment values, and categories
const emotionDetails: Record<Emotion, { emoji: string; sentimentValue: number; category: SentimentCategory }> = {
  anger: { emoji: '😠', sentimentValue: -0.9, category: 'negative' },
  confusion: { emoji: '😕', sentimentValue: 0.1, category: 'neutral' },
  desire: { emoji: '🧚', sentimentValue: 0.7, category: 'positive' },
  disgust: { emoji: '🤮', sentimentValue: -0.8, category: 'negative' },
  fear: { emoji: '😨', sentimentValue: -0.7, category: 'negative' },
  guilt: { emoji: '😔', sentimentValue: -0.6, category: 'negative' },
  happiness: { emoji: '😊', sentimentValue: 1.0, category: 'positive' },
  love: { emoji: '❤️', sentimentValue: 0.9, category: 'positive' },
  neutral: { emoji: '😐', sentimentValue: 0.0, category: 'neutral' },
  sadness: { emoji: '😢', sentimentValue: -1.0, category: 'negative' },
  sarcasm: { emoji: '🙄', sentimentValue: -0.2, category: 'neutral' },
  shame: { emoji: '😳', sentimentValue: -0.8, category: 'negative' },
  surprise: { emoji: '😲', sentimentValue: 0.6, category: 'positive' },
};

// Company name to be used in texts
const companyName = "InnovateCo";

// Example texts
const exampleTexts: { text: string; inferredEmotion: Emotion }[] = [
  { text: `I am so happy today because of ${companyName}!`, inferredEmotion: 'happiness' },
  { text: `This update from ${companyName} is absolutely brilliant!`, inferredEmotion: 'happiness' },
  { text: `I'm really confused by ${companyName}'s recent policy changes.`, inferredEmotion: 'confusion' },
  { text: `I desire to work for ${companyName}, their culture seems amazing.`, inferredEmotion: 'desire' },
  { text: `The customer service from ${companyName} was truly disgusting.`, inferredEmotion: 'disgust' },
  { text: `I fear ${companyName} might be losing its edge in the market.`, inferredEmotion: 'fear' },
  { text: `I feel so much guilt for not supporting ${companyName}'s charity drive.`, inferredEmotion: 'guilt' },
  { text: `I love everything ${companyName} stands for.`, inferredEmotion: 'love' },
  { text: `${companyName} released an update today.`, inferredEmotion: 'neutral' },
  { text: `This news from ${companyName} makes me so sad.`, inferredEmotion: 'sadness' },
  { text: `Oh, ${companyName} is innovative, alright... (sarcasm)`, inferredEmotion: 'sarcasm' },
  { text: `I feel shame for how ${companyName} handled that situation.`, inferredEmotion: 'shame' },
  { text: `Wow, ${companyName} really surprised me with that announcement!`, inferredEmotion: 'surprise' },
  { text: `${companyName}'s latest move just makes me angry!`, inferredEmotion: 'anger' },
  { text: `I'm so thrilled with ${companyName}'s impact on the community.`, inferredEmotion: 'happiness' },
  { text: `Another day, another update from ${companyName}. Nothing special.`, inferredEmotion: 'neutral' },
  { text: `The frustration I feel with ${companyName} is immense.`, inferredEmotion: 'anger' },
  { text: `I was completely taken aback by ${companyName}'s generosity.`, inferredEmotion: 'surprise' },
  { text: `Cannot believe ${companyName} would do this.`, inferredEmotion: 'disgust' },
  { text: `I've been thinking a lot about ${companyName}'s future.`, inferredEmotion: 'neutral' },
  { text: `Such a lovely gesture from ${companyName}. My heart is full!`, inferredEmotion: 'love' },
  { text: `Why is ${companyName} like this? So confused.`, inferredEmotion: 'confusion' },
  { text: `Absolutely furious with ${companyName} right now.`, inferredEmotion: 'anger' },
  { text: `I genuinely wish ${companyName} would reconsider.`, inferredEmotion: 'desire' },
];

// Emotion API integration
async function getEmotion(text: string, setApiStatus: (status: 'connected' | 'disconnected' | 'unknown') => void): Promise<{ emotion: Emotion; confidence: number }> {
  try {
    const response = await fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();
    
    // Map API response to our emotion types
    const emotionMap: Record<string, Emotion> = {
      'joy': 'happiness',
      'sadness': 'sadness',
      'anger': 'anger',
      'fear': 'fear',
      'surprise': 'surprise',
      'disgust': 'disgust',
      'love': 'love',
      'neutral': 'neutral',
      'confusion': 'confusion',
      'guilt': 'guilt',
      'shame': 'shame',
      'desire': 'desire',
      'sarcasm': 'sarcasm'
    };

    const detectedEmotion = emotionMap[data.emotion] || 'neutral';
    const confidence = data.confidence || 0.5;

    // Update API status to connected
    setApiStatus('connected');

    return { emotion: detectedEmotion, confidence };
  } catch (error) {
    console.error('Emotion API error:', error);
    
    // Update API status to disconnected
    setApiStatus('disconnected');
    
    // Fallback to mock detection if API is unavailable
    const lowerText = text.toLowerCase();
    let detectedEmotion: Emotion = 'neutral';
    let confidence = 0.7;
    
    if (lowerText.includes('happy') || lowerText.includes('brilliant') || lowerText.includes('thrilled')) {
      detectedEmotion = 'happiness';
      confidence = 0.9;
    } else if (lowerText.includes('angry') || lowerText.includes('furious') || lowerText.includes('frustration')) {
      detectedEmotion = 'anger';
      confidence = 0.8;
    } else if (lowerText.includes('confused') || lowerText.includes('confusion')) {
      detectedEmotion = 'confusion';
      confidence = 0.85;
    } else if (lowerText.includes('love') || lowerText.includes('lovely')) {
      detectedEmotion = 'love';
      confidence = 0.9;
    } else if (lowerText.includes('sad') || lowerText.includes('sadness')) {
      detectedEmotion = 'sadness';
      confidence = 0.8;
    } else if (lowerText.includes('fear') || lowerText.includes('afraid')) {
      detectedEmotion = 'fear';
      confidence = 0.75;
    } else if (lowerText.includes('surprised') || lowerText.includes('wow')) {
      detectedEmotion = 'surprise';
      confidence = 0.8;
    } else if (lowerText.includes('disgusting') || lowerText.includes('cannot believe')) {
      detectedEmotion = 'disgust';
      confidence = 0.85;
    } else if (lowerText.includes('guilt')) {
      detectedEmotion = 'guilt';
      confidence = 0.75;
    } else if (lowerText.includes('shame')) {
      detectedEmotion = 'shame';
      confidence = 0.8;
    } else if (lowerText.includes('desire') || lowerText.includes('wish')) {
      detectedEmotion = 'desire';
      confidence = 0.7;
    } else if (lowerText.includes('sarcasm') || lowerText.includes('alright...')) {
      detectedEmotion = 'sarcasm';
      confidence = 0.6;
    } else {
      // Random emotion for neutral-looking text
      const emotions = Object.keys(emotionDetails) as Emotion[];
      detectedEmotion = emotions[Math.floor(Math.random() * emotions.length)];
      confidence = 0.3 + Math.random() * 0.4;
    }
    
    return { emotion: detectedEmotion, confidence };
  }
}

// Message Card Component
const MessageCard: React.FC<{ message: Message }> = ({ message }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  let bgGradient = '';
  let textColorClass = '';
  let borderGlow = '';

  switch (message.sentimentCategory) {
    case 'positive':
      bgGradient = 'bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50';
      textColorClass = 'text-emerald-900';
      borderGlow = 'border-emerald-200 shadow-emerald-100';
      break;
    case 'negative':
      bgGradient = 'bg-gradient-to-br from-rose-50 via-red-50 to-pink-50';
      textColorClass = 'text-rose-900';
      borderGlow = 'border-rose-200 shadow-rose-100';
      break;
    case 'neutral':
    default:
      bgGradient = 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50';
      textColorClass = 'text-slate-900';
      borderGlow = 'border-slate-200 shadow-slate-100';
      break;
  }

  return (
    <div className={`transform transition-all duration-300 ease-out ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'}`}>
      <div className={`flex items-start p-3 rounded-xl border ${bgGradient} ${borderGlow} shadow-md hover:shadow-lg transition-all duration-200 hover:scale-[1.01]`}>
        <div className="flex-shrink-0 text-lg pr-3 pt-0.5">{message.emoji}</div>
        <div className="flex-grow min-w-0">
          <p className={`font-medium ${textColorClass} text-sm leading-relaxed mb-2`}>{message.text}</p>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="px-2 py-0.5 bg-white/80 rounded-full border font-bold capitalize">
              {message.emotion}
            </span>
            <span className="px-2 py-0.5 bg-white/80 rounded-full border font-bold">
              {(message.confidence * 100).toFixed(0)}%
            </span>
            <span className={`px-2 py-0.5 rounded-full font-bold ${
              message.sentimentValue > 0.2 ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 
              message.sentimentValue < -0.2 ? 'bg-rose-100 text-rose-800 border border-rose-200' : 'bg-amber-100 text-amber-800 border border-amber-200'
            }`}>
              {message.sentimentValue > 0 ? '+' : ''}{message.sentimentValue.toFixed(2)}
            </span>
            <span className="text-gray-500 text-xs">
              {message.timestamp.toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Component
export default function SocialMediaSentimentMonitor() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [overallSentiment, setOverallSentiment] = useState<number>(0);
  const [speedMultiplier, setSpeedMultiplier] = useState<number>(1);
  const [tps, setTps] = useState<number>(0);
  const [totalMessages, setTotalMessages] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(true);
  const [startTime] = useState<number>(Date.now());
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'unknown'>('unknown');
  const [recentMessages, setRecentMessages] = useState<number[]>([]);
  const MAX_MESSAGES = 30;

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Real-time TPS calculation based on recent message timestamps
  useEffect(() => {
    const tpsInterval = setInterval(() => {
      const now = Date.now();
      const oneSecondAgo = now - 1000;
      
      // Filter messages from the last second
      const messagesInLastSecond = recentMessages.filter(timestamp => timestamp > oneSecondAgo);
      setTps(messagesInLastSecond.length);
      
      // Clean up old timestamps (keep only last 5 seconds of data)
      const fiveSecondsAgo = now - 5000;
      setRecentMessages(prev => prev.filter(timestamp => timestamp > fiveSecondsAgo));
    }, 100); // Update every 100ms for smoother updates

    return () => clearInterval(tpsInterval);
  }, [recentMessages]);

  // Generate a single message
  const generateSingleMessage = async () => {
    const randomText = exampleTexts[Math.floor(Math.random() * exampleTexts.length)].text;
    
    try {
      const { emotion, confidence } = await getEmotion(randomText, setApiStatus);
      const detail = emotionDetails[emotion];
      
      const newMessage: Message = {
        id: `${Date.now()}-${Math.random()}`,
        text: randomText,
        emotion,
        emoji: detail.emoji,
        confidence,
        sentimentValue: detail.sentimentValue,
        sentimentCategory: detail.category,
        timestamp: new Date(),
      };

      setMessages(prev => {
        const updated = [...prev, newMessage];
        return updated.slice(-MAX_MESSAGES);
      });

      setTotalMessages(prev => prev + 1);
      
      // Add timestamp for TPS calculation
      setRecentMessages(prev => [...prev, Date.now()]);
    } catch (error) {
      console.error('Error generating message:', error);
      setTotalMessages(prev => prev + 1);
      // Still add timestamp even if there's an error, to maintain accurate TPS
      setRecentMessages(prev => [...prev, Date.now()]);
    }
  };

  // Main interval effect for message generation
  useEffect(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (isRunning && speedMultiplier > 0) {
      const intervalTime = Math.max(10, 1000 / speedMultiplier);
      
      const scheduleNextMessage = () => {
        intervalRef.current = setTimeout(async () => {
          try {
            await generateSingleMessage();
          } catch (error) {
            console.error('Error in message generation:', error);
          }
          // Schedule the next message after this one completes
          scheduleNextMessage();
        }, intervalTime);
      };
      
      scheduleNextMessage();
    }

    return () => {
      if (intervalRef.current) {
        clearTimeout(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [speedMultiplier, isRunning]);

  // Sentiment calculation
  useEffect(() => {
    if (messages.length > 0) {
      const total = messages.reduce((sum, msg) => sum + msg.sentimentValue, 0);
      setOverallSentiment(total / messages.length);
    }
  }, [messages]);

  // Speed control handlers
  const handleSpeedChange = (newSpeed: number) => {
    setSpeedMultiplier(newSpeed);
    setIsRunning(newSpeed > 0);
    
    // Reset TPS when speed changes for more accurate immediate readings
    if (newSpeed === 0) {
      setTps(0);
      setRecentMessages([]);
    }
  };

  const gaugePosition = ((overallSentiment + 1) / 2) * 100;
  const getSentimentColor = () => {
    if (overallSentiment > 0.3) return 'text-emerald-600';
    if (overallSentiment < -0.3) return 'text-rose-600';
    return 'text-amber-600';
  };

  const getSentimentBg = () => {
    if (overallSentiment > 0.3) return 'from-emerald-500 to-green-500';
    if (overallSentiment < -0.3) return 'from-rose-500 to-red-500';
    return 'from-amber-500 to-yellow-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Compact Header */}
        <div className="text-center mb-6">
          <h1 className="text-3xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            {companyName} Sentiment Monitor
          </h1>
          <div className={`inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold backdrop-blur-sm border ${
            apiStatus === 'connected' 
              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-400' 
              : apiStatus === 'disconnected' 
                ? 'bg-rose-500/20 text-rose-300 border-rose-400' 
                : 'bg-amber-500/20 text-amber-300 border-amber-400'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              apiStatus === 'connected' ? 'bg-emerald-400' : 
              apiStatus === 'disconnected' ? 'bg-rose-400' : 'bg-amber-400'
            }`}></div>
            {apiStatus === 'connected' ? 'API Connected' : 
             apiStatus === 'disconnected' ? 'Fallback Mode' : 
             'Checking...'}
          </div>
        </div>

        {/* Compact Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="group relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-300"></div>
            <div className="relative bg-slate-800/90 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
              <div className="text-center">
                <div className="text-2xl font-black text-cyan-400 mb-1">{tps.toFixed(1)}</div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Msg/Sec</div>
                <div className="w-full bg-slate-700 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full transition-all duration-1000"
                    style={{width: `${Math.min(100, (tps / 20) * 100)}%`}}
                  ></div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="group relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-green-500 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-300"></div>
            <div className="relative bg-slate-800/90 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
              <div className="text-center">
                <div className="text-2xl font-black text-emerald-400 mb-1">{totalMessages.toLocaleString()}</div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Total</div>
                <div className="text-emerald-400 text-xs">Messages processed</div>
              </div>
            </div>
          </div>
          
          <div className="group relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-300"></div>
            <div className="relative bg-slate-800/90 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
              <div className="text-center">
                <div className="text-2xl font-black text-purple-400 mb-1">
                  {speedMultiplier === 0 ? '⏸️' : `${speedMultiplier}×`}
                </div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Speed</div>
                <div className={`text-xs font-bold ${
                  speedMultiplier === 0 ? 'text-slate-400' : 
                  speedMultiplier >= 20 ? 'text-pink-400' : 
                  speedMultiplier >= 10 ? 'text-red-400' : 'text-purple-400'
                }`}>
                  {speedMultiplier === 0 ? 'Paused' : 
                   speedMultiplier >= 20 ? 'LUDICROUS!' : 
                   speedMultiplier >= 10 ? 'INSANE!' : 'Active'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Compact Speed Control Panel */}
        <div className="mb-6">
          <div className="relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl blur opacity-20"></div>
            <div className="relative bg-slate-800/95 backdrop-blur-sm rounded-2xl p-4 border border-slate-600/50">
              <h3 className="text-lg font-bold text-center text-slate-100 mb-4 bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
                Speed Control
              </h3>
              <div className="grid grid-cols-4 lg:grid-cols-8 gap-2">
                {[
                  { speed: 0, label: 'Pause', icon: '⏸️', color: 'from-slate-500 to-slate-600' },
                  { speed: 0.5, label: 'Slow', icon: '🐌', color: 'from-blue-500 to-blue-600' },
                  { speed: 1, label: 'Normal', icon: '⚡', color: 'from-green-500 to-green-600' },
                  { speed: 2, label: 'Fast', icon: '🚀', color: 'from-yellow-500 to-yellow-600' },
                  { speed: 5, label: 'Ultra', icon: '💥', color: 'from-orange-500 to-red-500' },
                  { speed: 10, label: 'INSANE', icon: '🔥', color: 'from-red-500 to-pink-500' },
                  { speed: 20, label: 'LUDICROUS', icon: '⚡', color: 'from-pink-500 to-purple-500' },
                  { speed: 50, label: 'MAXIMUM', icon: '💀', color: 'from-purple-500 to-violet-500' }
                ].map(({ speed, label, icon, color }) => (
                  <button
                    key={speed}
                    onClick={() => handleSpeedChange(speed)}
                    className={`group relative p-2 rounded-lg font-bold text-white text-xs transition-all duration-300 transform hover:scale-105 ${
                      speedMultiplier === speed 
                        ? `bg-gradient-to-br ${color} ring-2 ring-white/50 shadow-lg scale-105` 
                        : `bg-gradient-to-br ${color} hover:shadow-md opacity-80 hover:opacity-100`
                    }`}
                  >
                    <div className="text-lg mb-1">{icon}</div>
                    <div className="text-xs font-black uppercase">{label}</div>
                    <div className="text-xs opacity-90">{speed}×</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Compact Sentiment Gauge */}
        <div className="mb-6">
          <div className="relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-rose-500 via-yellow-500 to-emerald-500 rounded-2xl blur opacity-20"></div>
            <div className="relative bg-slate-800/95 backdrop-blur-sm rounded-2xl p-4 border border-slate-600/50">
              <h2 className="text-lg font-bold text-center text-slate-100 mb-4">
                Sentiment: <span className={`${getSentimentColor()}`}>{overallSentiment.toFixed(2)}</span>
              </h2>
              <div className="relative h-4 bg-gradient-to-r from-rose-200 via-yellow-200 to-emerald-200 rounded-full overflow-hidden shadow-inner">
                <div
                  className={`h-full bg-gradient-to-r ${getSentimentBg()} rounded-full transition-all duration-1000 ease-out shadow-lg relative`}
                  style={{ 
                    width: `${gaugePosition}%`,
                    minWidth: '4px'
                  }}
                >
                  <div className="absolute inset-0 bg-white/20 animate-pulse rounded-full"></div>
                </div>
                <div 
                  className="absolute top-0 w-0.5 h-full bg-white shadow-lg transition-all duration-1000"
                  style={{ left: `${gaugePosition}%` }}
                >
                  <div className="w-2 h-2 bg-white rounded-full -mt-1 -ml-1 shadow-lg border border-slate-600"></div>
                </div>
              </div>
              <div className="flex justify-between text-xs font-bold mt-2">
                <span className="text-rose-400">Negative</span>
                <span className="text-slate-400">Neutral</span>
                <span className="text-emerald-400">Positive</span>
              </div>
            </div>
          </div>
        </div>

        {/* Compact Messages Feed */}
        <div className="relative">
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-15"></div>
          <div className="relative bg-slate-800/95 backdrop-blur-sm rounded-2xl border border-slate-600/50 overflow-hidden">
            <div className="p-4 pb-2">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-slate-100">🌊 Live Feed</h2>
                <div className="px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full text-sm font-bold">
                  {messages.length}
                </div>
              </div>
            </div>
            
            <div className="px-4 pb-4 max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
              {messages.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-4xl mb-3 animate-bounce">🔄</div>
                  <div className="text-lg font-bold text-slate-300 mb-2">
                    {isRunning ? '🌟 Analyzing...' : '⏸️ Paused'}
                  </div>
                  <div className="text-sm text-slate-400">
                    {isRunning ? 'Real-time sentiment detection' : 'Select speed to begin'}
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {messages.map((msg, index) => (
                    <div key={msg.id} style={{ animationDelay: `${index * 50}ms` }}>
                      <MessageCard message={msg} />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
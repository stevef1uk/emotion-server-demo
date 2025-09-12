import { useState, useEffect, useCallback, useRef } from 'react';

interface Emotion {
  name: string;
  emoji: string;
  keywords: string[];
}

const emotions: Emotion[] = [
  { name: 'anger', emoji: '😡', keywords: ['angry', 'mad', 'frustrated', 'rage', 'furious'] },
  { name: 'confusion', emoji: '😕', keywords: ['confused', 'puzzled', 'unclear', 'baffled', 'huh'] },
  { name: 'desire', emoji: '🧚', keywords: ['want', 'wish', 'desire', 'need', 'crave'] },
  { name: 'disgust', emoji: '🤢', keywords: ['disgusting', 'gross', 'nasty', 'repulsive', 'ugh'] },
  { name: 'fear', emoji: '😨', keywords: ['scared', 'fear', 'afraid', 'terrified', 'anxious'] },
  { name: 'guilt', emoji: '😔', keywords: ['guilty', 'sorry', 'apologize', 'regret', 'bad'] },
  { name: 'happiness', emoji: '😊', keywords: ['happy', 'joy', 'glad', 'pleased', 'delighted'] },
  { name: 'love', emoji: '❤️', keywords: ['love', 'adore', 'fond', 'beloved', 'cherish'] },
  { name: 'neutral', emoji: '😐', keywords: ['ok', 'fine', 'neutral', 'alright', 'indifferent'] },
  { name: 'sadness', emoji: '😢', keywords: ['sad', 'unhappy', 'down', 'depressed', 'gloomy'] },
  { name: 'sarcasm', emoji: '🤨', keywords: ['sarcastic', 'ironic', 'sure', 'obviously'] },
  { name: 'shame', emoji: '😳', keywords: ['ashamed', 'embarrassed', 'humiliated', 'mortified'] },
  { name: 'surprise', emoji: '😲', keywords: ['surprise', 'shocked', 'wow', 'unexpected', 'astonished'] },
];

function CustomerChatAgent() {
  const [inputText, setInputText] = useState<string>('');
  const [highlightedEmotion, setHighlightedEmotion] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const detectEmotion = useCallback(async (textToAnalyze: string) => {
    if (!textToAnalyze.trim()) {
      setHighlightedEmotion(null);
      return;
    }

    setIsProcessing(true);
    // Simulate API call delay with a Promise
    await new Promise(resolve => setTimeout(resolve, 500));

    let matchedEmotion: string | null = null;
    const lowerCaseText = textToAnalyze.toLowerCase();

    // Regex to find complete sentences (ending with . ! ?)
    // It captures sentences including their punctuation, ensuring we only analyze complete thoughts.
    // Example: "Hello. How are you? I'm fine!" will be split into ["Hello.", " How are you?", " I'm fine!"]
    const completeSentences = lowerCaseText.match(/[^.!?]+[.!?]+/g) || [];

    for (const sentence of completeSentences) {
      // Trim to clean up potential leading/trailing spaces from the regex match
      const trimmedSentence = sentence.trim(); 
      for (const emotion of emotions) {
        for (const keyword of emotion.keywords) {
          // Check if the keyword exists as a whole word within the complete sentence
          // Using \b for word boundaries to prevent partial matches (e.g., "sad" in "saddle")
          const regex = new RegExp(`\\b${keyword}\\b`, 'g');
          if (regex.test(trimmedSentence)) {
            matchedEmotion = emotion.name;
            break; // Found a keyword for this emotion in this sentence
          }
        }
        if (matchedEmotion) break; // Found an emotion match, no need to check other emotions
      }
      if (matchedEmotion) break; // Found an emotion match in one of the sentences, no need to check other sentences
    }

    setHighlightedEmotion(matchedEmotion);
    setIsProcessing(false);
  }, []); // 'emotions' array is a constant, so no dependency needed for useCallback for stability

  useEffect(() => {
    // Clear any existing debounce timer
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    if (inputText.trim()) {
      // Set a new timeout to call detectEmotion after a pause in typing
      debounceTimeoutRef.current = setTimeout(() => {
        detectEmotion(inputText);
      }, 700); // 700ms debounce time
    } else {
      // If the input text is empty, clear any previously highlighted emotion
      setHighlightedEmotion(null);
    }

    // Cleanup function: This runs when the component unmounts or before the useEffect
    // re-runs due to a dependency change. It ensures no pending timeouts persist.
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [inputText, detectEmotion]); // Dependencies: inputText changes, or detectEmotion (which is stable via useCallback)

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(event.target.value);
  };

  return (
    <div className="flex flex-col max-w-lg mx-auto bg-white rounded-xl shadow-lg p-6 m-6 border border-gray-200">
      <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">Customer Chat Agent</h2>

      {/* Emotion Icons Display */}
      <div className="flex flex-wrap justify-center gap-3 p-3 mb-6 bg-gray-50 rounded-lg border border-gray-100">
        {emotions.map((emotion) => (
          <div
            key={emotion.name}
            className={`
              flex flex-col items-center p-2 rounded-md
              transition-colors duration-200 ease-in-out
              ${highlightedEmotion === emotion.name
                ? 'bg-indigo-100 text-indigo-700 shadow-md transform scale-105' // Highlighted state
                : 'bg-white text-gray-500 hover:bg-gray-50 hover:text-gray-700' // Default state
              }
            `}
            title={emotion.name}
          >
            <span className="text-3xl leading-none">{emotion.emoji}</span>
            <span className={`text-xs font-medium mt-1 ${highlightedEmotion === emotion.name ? 'text-indigo-700' : 'text-gray-600'}`}>
              {emotion.name}
            </span>
          </div>
        ))}
      </div>

      {/* Text Input Area */}
      <div className="relative mb-4">
        <textarea
          className="w-full p-3 pr-10 text-gray-700 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent transition-all duration-200 ease-in-out resize-none h-32"
          placeholder={isProcessing ? "Analyzing sentiment..." : "Type your message here..."}
          value={inputText}
          onChange={handleInputChange}
          disabled={isProcessing} // Disable input while processing
        />
        {/* Processing Indicator */}
        {isProcessing && (
          <div className="absolute top-3 right-3 text-indigo-500 animate-pulse" title="Analyzing...">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        )}
      </div>

      {/* Detected Emotion Display */}
      <div className="text-sm text-gray-600 text-center">
        {highlightedEmotion ? (
          <p className="font-semibold text-indigo-600">Detected Emotion: {highlightedEmotion} {emotions.find(e => e.name === highlightedEmotion)?.emoji}</p>
        ) : (
          <p>Start typing to detect emotions in complete sentences.</p>
        )}
      </div>
    </div>
  );
}

export default CustomerChatAgent;
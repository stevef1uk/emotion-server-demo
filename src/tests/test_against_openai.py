import json
import requests
import openai
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from datasets import load_dataset
from transformers import pipeline
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
import time
import random
from collections import defaultdict

class EmotionComparison:
    def __init__(self, openai_api_key: str, your_api_url: str = "http://localhost:8000/predict"):
        """
        Initialize the emotion comparison tool
        
        Args:
            openai_api_key: Your OpenAI API key
            your_api_url: URL of your emotion API service
        """
        self.openai_api_key = openai_api_key
        self.your_api_url = your_api_url
        
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Emotion mapping
        self.emotions = {
            'anger': '😡', 'confusion': '😕', 'desire': '🧚', 'disgust': '🤢',
            'fear': '😨', 'guilt': '😔', 'happiness': '😊', 'love': '❤️',
            'neutral': '😐', 'sadness': '😢', 'sarcasm': '🤨', 'shame': '😳',
            'surprise': '😲'
        }
        
        # Map Hugging Face model labels to our standard labels
        # Note: The HF model only supports a subset of our emotions
        self.hf_emotion_map = {
            'sadness': 'sadness', 'joy': 'happiness', 'love': 'love', 
            'anger': 'anger', 'fear': 'fear', 'surprise': 'surprise'
        }

        # Non-obvious text samples for each emotion (few hundred words each)
        self.test_samples = self._generate_test_samples()

        # Initialize Hugging Face model pipeline
        print("📥 Initializing Hugging Face model pipeline...")
        self.hf_classifier = pipeline(
            "text-classification", 
            model="bhadresh-savani/distilbert-base-uncased-emotion",
            return_all_scores=False
        )
        print("✅ Hugging Face model loaded.")
        
    def _generate_test_samples(self) -> Dict[str, List[str]]:
        """Generate realistic, non-obvious text samples for each emotion category"""
        
        # Your custom samples... (same as before)
        samples = {
            'anger': [
                "The meeting went on for three hours without any real progress. Every suggestion I made was immediately shot down without consideration. My colleague kept interrupting me mid-sentence, and when I finally got to present my proposal, the manager had already decided to go with someone else's half-baked idea. I've been working on this project for months, putting in extra hours, researching every detail, and it feels like none of that matters. The company keeps talking about valuing employee input, but when it comes down to it, it's always the same people whose voices get heard. I left the conference room and went straight to my desk, trying to focus on other tasks, but I couldn't concentrate. The way they dismissed my work so casually made my jaw clench. I've been with this company for five years, and I'm starting to wonder if my efforts are even noticed.",
                "Traffic was backed up for miles because of construction that started without any warning signs. I've been sitting in my car for forty-five minutes, watching the gas gauge drop while the engine idles. The radio keeps playing the same annoying commercial over and over. My phone is buzzing with messages from my boss asking where I am, but there's nothing I can do about it. The construction workers seem to be moving in slow motion, taking breaks every few minutes. Meanwhile, cars are honking constantly, adding to the chaos. I had planned to stop by the grocery store after work, but at this rate, everything will be closed by the time I get there. This is the third time this week that poor city planning has completely derailed my schedule. The worst part is knowing this could have been avoided with proper communication.",
            ],
            'confusion': [
                "I've been staring at this instruction manual for the past hour, and nothing seems to make sense. Step three refers to part B, but part B isn't mentioned until step seven. The diagram shows components that don't match what's in the box, and the troubleshooting section assumes I've already completed steps that aren't listed anywhere. I've tried following the online tutorial, but it's for a completely different model. The customer service chat bot keeps giving me generic responses that don't address my specific questions. My neighbor said he assembled the same item last year, but when I asked for advice, his explanation only made things more complicated. I'm usually pretty good at figuring these things out, but this time I feel like I'm missing some crucial piece of information that everyone else seems to know instinctively.",
                "The professor's lecture today covered concepts that weren't in any of our assigned readings. She kept referencing theories from previous courses that half the class never took. When students asked questions, her answers seemed to contradict points she made earlier in the semester. The syllabus mentions a midterm exam, but she hasn't provided any study guide or indication of what topics will be covered. My classmates and I compared notes afterward, and we all came away with different interpretations of the main points. The textbook explains things one way, but her lectures seem to approach the subject from a completely different angle. I've attended every class and done all the readings, but I feel like I'm constantly missing connections that should be obvious.",
            ],
            'desire': [
                "Walking through the old bookstore downtown, I discovered a leather-bound journal with blank pages that seemed to call out to me. The way the afternoon light filtered through the dusty windows created the perfect atmosphere for writing. I imagined myself sitting in a cozy café, filling those pages with stories that have been floating around in my mind for months. The owner mentioned that several famous authors used to browse these same shelves when they were starting out. There's something magical about the smell of old books and the quiet rustle of pages turning. I picture myself returning here regularly, becoming part of the community of writers and readers who gather for poetry readings on Thursday nights. The journal would be the first step toward finally pursuing the creative writing that I've always dreamed about but never made time for.",
                "The travel documentary showed cobblestone streets winding through ancient villages where time seems to have stopped centuries ago. Market vendors were selling fresh produce and handmade crafts while children played in fountain squares surrounded by medieval architecture. I found myself researching flight prices and accommodation options before the program even ended. The idea of waking up to church bells instead of traffic, exploring hidden museums and family-run restaurants, feels like exactly the adventure I need. My savings account has been growing steadily, and I have enough vacation days accumulated to make a two-week trip possible. I envision myself sketching in a notebook while sitting at sidewalk cafés, striking up conversations with locals, and discovering places that aren't mentioned in any guidebook.",
            ],
            'disgust': [
                "The restaurant had excellent reviews online, but the reality was quite different. Our table was sticky despite supposedly being cleaned, and there were crumbs from previous customers still scattered around the booth. The server's apron was stained, and when she brought our drinks, I noticed her fingernails were dirty. The bathroom was even worse - paper towels overflowing from the dispenser, soap dispensers that were empty, and an overwhelming smell that made me want to leave immediately. When our food finally arrived, my pasta was swimming in grease, and my partner's salad had wilted lettuce with brown edges. The whole experience made me lose my appetite completely. We left most of our meals untouched and paid the bill as quickly as possible. I couldn't stop thinking about the poor hygiene standards for the rest of the evening.",
                "Cleaning out my grandmother's attic after she moved to assisted living revealed decades of accumulated items in various states of decay. Boxes of old magazines had become damp and moldy, creating a musty smell that made my eyes water. I found containers of expired food from years ago, some with contents I couldn't identify anymore. The insulation was falling down in chunks, and there were signs that rodents had made themselves at home among the stored belongings. Every item I touched left my hands grimy, and I had to take frequent breaks to get fresh air. Old fabrics had developed stains of unknown origin, and several pieces of furniture were covered in a thick layer of dust mixed with what looked like animal droppings. The whole process made me appreciate the importance of regular cleaning and organization.",
            ],
            'fear': [
                "The power went out during the storm while I was home alone, and the backup generator failed to kick in. My phone battery was at fifteen percent, and the landline wasn't working either. Through the windows, I could see trees bending at dangerous angles in the wind, and something heavy crashed onto the roof above my bedroom. The weather radio announced tornado warnings for the entire county, advising everyone to seek shelter in interior rooms. I gathered flashlights and water bottles, heading to the basement where I could hear the house creaking and groaning above me. Every few minutes, another crash or bang made me wonder if the windows were holding up. The storm seemed to go on forever, and I kept checking my phone for updates, watching the battery percentage drop steadily. Being cut off from communication while severe weather raged outside made me realize how vulnerable we really are.",
                "Walking home from work later than usual, I noticed the same car had been behind me for several blocks, making the same turns I was making. The street lights were dim, and most of the businesses had closed for the day, leaving long stretches of sidewalk poorly lit. My usual route seemed different somehow, more isolated and threatening than during daylight hours. I tried varying my pace and taking a slightly different path, but the headlights continued to follow at a consistent distance. My keys were ready in my hand, and I had my phone out, trying to look casual while actually preparing to call for help if necessary. The familiar neighborhood suddenly felt foreign and unpredictable. When I finally reached my building and the car continued past, I felt relieved but shaken, realizing how much we take our daily sense of security for granted.",
            ],
            'guilt': [
                "My elderly neighbor has been asking for help with her garden for weeks, and I keep telling her I'll stop by when I have time. She's been struggling to maintain the flower beds that her late husband planted, and I can see from my kitchen window that the weeds are taking over. Yesterday, she slipped while trying to carry a heavy watering can and scraped her knee badly. If I had just spent an hour helping her last weekend like I promised, she wouldn't have been out there alone trying to manage tasks that are becoming too difficult for her. I have the tools and the physical ability to help, but I've been prioritizing my own projects and entertainment over her genuine need for assistance. She never complains or makes me feel bad about it, which somehow makes it worse. I know she's too proud to ask anyone else, and I'm probably the only neighbor she feels comfortable approaching.",
                "During the family dinner, my teenage nephew was excitedly telling everyone about his first job interview, and I made a joke about his nervousness that came out sounding more critical than I intended. The conversation moved on to other topics, but I noticed he became quiet for the rest of the evening and avoided making eye contact with me. Later, my sister mentioned that he had been really anxious about the interview and was hoping for encouragement from the adults in his life. I realized that my attempt at humor had probably reinforced his insecurities instead of helping him feel more confident. He looks up to me as someone who's established in their career, and I missed an opportunity to be supportive during an important milestone in his life. The worst part is that I recognized his nervousness because I remember feeling exactly the same way at his age.",
            ],
            'happiness': [
                "This morning, I received a call from my college roommate who I hadn't spoken to in over two years. She was traveling through my city for work and wondered if we could meet for coffee during her layover. Even though it meant rearranging my entire afternoon schedule, I couldn't pass up the chance to reconnect. We met at the airport café and ended up talking for three hours straight, sharing stories about career changes, relationships, and all the adventures we've had since graduation. It felt like no time had passed at all, and we were laughing about the same silly things that used to crack us up in our dorm room. She showed me pictures from her recent hiking trip in Colorado, and I told her about the cooking classes I've been taking on weekends. By the time she had to catch her connecting flight, we had already made plans for me to visit her next month. Sometimes the best moments are the completely unexpected ones.",
                "After months of practice, I finally managed to play through the entire piano piece without making any major mistakes. My fingers found the right keys instinctively, and for the first time, I felt like I was actually making music instead of just hitting notes in the correct sequence. The melody flowed naturally, and I could hear the emotional nuances that had been hidden beneath my earlier clumsy attempts. My instructor had been encouraging but honest about areas that needed work, so when she smiled and nodded during today's lesson, I knew it was genuine approval. The piece that once seemed impossibly complex now feels like a natural extension of what my hands want to do. I've been looking forward to these weekly lessons more than almost anything else in my schedule, and today reminded me why learning new skills as an adult can be so rewarding.",
            ],
            'love': [
                "Watching my partner teach our daughter how to ride her bicycle reminded me of all the reasons I fell for them in the first place. Their patience was endless as she wobbled and hesitated, and they celebrated every small improvement with genuine enthusiasm. When she finally pedaled a full circle around the driveway without falling, the pride and joy on both their faces made my heart feel like it might burst. Later, as we sat on the porch while she practiced more, my partner reached over and squeezed my hand, and we shared one of those perfect moments of contentment that make all the challenging parts of life seem worthwhile. The way they love our daughter so completely, and the way that love extends to creating a warm, safe home for all of us, reminds me daily how fortunate I am to share this life with them. These ordinary Sunday afternoons have become the most precious part of my week.",
                "My grandmother's letters arrived in a shoebox that my aunt found while cleaning out the family home. Reading her words from decades ago, addressed to my grandfather during his military service, revealed a love story I never knew existed. Her handwriting was elegant and careful, and every letter began with some variation of 'My dearest' followed by updates about daily life mixed with expressions of longing and devotion. She wrote about missing his laugh, saving newspaper clippings she thought would interest him, and counting the days until his return. The letters painted a picture of two people who genuinely delighted in each other's company and supported each other's dreams. Finding these intimate glimpses into their relationship helped me understand where the warmth and stability in our family originated, and made me appreciate the foundation of love that shaped my childhood.",
            ],
            'neutral': [
                "The quarterly budget meeting covered the usual topics: department spending, projected revenue for next year, and proposed changes to the office supply ordering system. We reviewed spreadsheets showing expense categories and discussed whether the current software licenses were cost-effective. The facilities manager presented options for updating the break room appliances, and we voted on which vendor to use for the annual equipment maintenance contracts. Most agenda items were straightforward administrative decisions that didn't require much debate. The meeting ended on schedule, and everyone returned to their regular work tasks. I updated my calendar with the implementation dates for the new procedures and filed the meeting notes with the other quarterly reports. It was a typical business meeting that accomplished its intended purpose without any unexpected developments or complications.",
                "I spent the afternoon organizing my digital photo collection, sorting images into folders by year and event. The process involved looking through thousands of pictures from vacations, family gatherings, and random moments I had captured over the past several years. Some photos were duplicates that I deleted to free up storage space, while others reminded me of experiences I had completely forgotten about. I created backup copies on an external drive and updated the file names to make them easier to find in the future. The task took longer than expected, but now everything is systematically arranged and properly labeled. It's one of those maintenance activities that isn't particularly exciting but feels satisfying to complete. I'll probably do the same thing with my music library next weekend.",
            ],
            'sadness': [
                "Walking past the old coffee shop where my best friend and I used to study for exams, I noticed they had changed the furniture and painted over the cozy brick walls we loved so much. The corner booth where we spent countless hours discussing everything from philosophy to career plans has been replaced with generic tables that look like every other chain restaurant. She moved across the country for a job opportunity six months ago, and we've been meaning to schedule regular video calls, but our different time zones and busy schedules make it difficult. The place holds so many memories of late-night conversations and shared dreams that seeing it transformed into something unrecognizable felt like losing another piece of our friendship. I ordered my usual drink, but even that tasted different somehow. Changes are inevitable, but sometimes they arrive before you're ready to let go of what came before.",
                "Packing up my father's workshop after his retirement revealed decades of carefully organized tools and half-finished projects that he'll never complete. Each drawer contained items he had collected over the years, thinking he might need them someday for repairs or creative endeavors. I found detailed sketches for a birdhouse he planned to build for my daughter, along with the wood he had already measured and cut to size. His handwriting was on labels throughout the space, categorizing screws and hardware with the same meticulous attention he brought to everything in his life. The workshop represented his identity as someone who could fix anything and create beautiful, functional objects with his hands. Dismantling this space felt like acknowledging that a chapter of his life, and ours as a family, was definitively ending.",
            ],
            'sarcasm': [
                "The company announced another 'exciting opportunity' for employees to demonstrate their commitment by working extra hours without additional compensation. Management emphasized how this voluntary overtime would really show who the 'team players' are and contribute to the 'family atmosphere' they're so proud of cultivating. They also mentioned that while budget constraints prevent them from offering monetary rewards, the experience itself would be incredibly valuable for professional development. The email concluded by noting that participation would definitely be taken into consideration during performance reviews, though they made sure to stress that it's entirely optional. During the mandatory meeting to discuss this wonderful opportunity, our supervisor explained how grateful we should feel to work for such an innovative company that provides so many chances for growth. The best part was when they suggested we should be excited about the opportunity to prove our dedication.",
                "My upstairs neighbor has discovered a new hobby that apparently requires moving furniture at three in the morning. The rhythmic dragging and dropping sounds suggest they're either redecorating their entire apartment or training for some kind of nocturnal weightlifting competition. When I politely mentioned the noise issue, they assured me they're just 'living their life' and shouldn't have to modify their schedule for anyone else's convenience. They also helpfully suggested I could try wearing earplugs if I'm such a light sleeper. It's wonderful to live below someone who's so considerate about sharing their passion for late-night interior design with the entire building. I'm sure all the other neighbors are equally appreciative of the free sound effects that accompany their attempt to sleep.",
            ],
            'shame': [
                "During the presentation to potential clients, I mispronounced the name of their company multiple times despite having it written clearly in my notes. The mistake became more noticeable each time I said it wrong, and I could see the executives exchanging glances across the conference table. When the meeting ended, my supervisor pulled me aside to discuss what had happened, explaining how important it is to get these basic details right when representing our firm. The clients were polite about it, but I know that small error probably undermined their confidence in our attention to detail and professionalism. I had spent weeks preparing the technical aspects of the proposal, but I overlooked something as fundamental as learning how to say their company name correctly. My colleagues have been supportive, but I keep replaying the moment and wishing I could have handled it differently. It's the kind of mistake that feels much bigger than it probably was.",
                "At the family reunion, my cousin asked about my career plans, and I found myself exaggerating my accomplishments and making up details about projects that don't actually exist. The conversation spiraled as I tried to make my life sound more impressive than it really is, creating an elaborate story about opportunities and achievements that were mostly wishful thinking. Other family members joined the discussion, asking follow-up questions that forced me to invent even more details to keep the story consistent. By the end of the evening, I had constructed an entirely fictional version of my professional life that bore little resemblance to reality. Later, I overheard my aunt telling someone else about my 'successful career,' and I realized I had created expectations that I could never live up to. The worst part is knowing that my actual accomplishments are perfectly respectable, but I felt compelled to embellish them anyway.",
            ],
            'surprise': [
                "Opening my laptop this morning, I discovered that the short story I submitted to a literary magazine three months ago had been accepted for publication. I had completely forgotten about it after weeks passed without any response, assuming it had been rejected like the previous submissions. The editor's email was enthusiastic and mentioned that they rarely receive pieces that capture their readers' attention so effectively. They want to feature my story in their upcoming themed issue and have invited me to contribute to future publications. I've been writing as a hobby for years, never really believing that anyone outside my immediate circle would appreciate my work. The acceptance letter included details about their publication timeline and even mentioned a small payment for contributors. It's the kind of news that makes you want to call everyone you know, but also feels too good to be true.",
                "Walking into what I thought was going to be a regular Tuesday morning staff meeting, I found my office decorated with balloons and my colleagues holding a cake with my name on it. Apparently, they had been planning a celebration for the promotion I received last week, and somehow managed to coordinate the surprise without me noticing any of the preparation. My supervisor made a speech about my contributions to the team, mentioning specific projects and qualities that I didn't realize had been noticed so thoroughly. The cake was from my favorite bakery across town, which meant someone had made a special trip to get exactly what they knew I would enjoy. Even the decoration theme reflected inside jokes and shared experiences from our team meetings over the past year. It was one of those moments that reminds you how much thought and care your colleagues put into making work feel like more than just a job.",
            ]
        }
        
        return samples

    def call_your_api(self, text: str) -> Dict:
        """Call your emotion API service"""
        try:
            response = requests.post(
                self.your_api_url,
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling your API: {e}")
            return {"emotion": "error", "confidence": 0}

    def call_chatgpt_api(self, text: str) -> Dict:
        """Call ChatGPT API for emotion classification using the new client syntax."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an emotion classifier. Classify the given text into one of these emotions: {', '.join(self.emotions.keys())}. 
                        
                        Respond with ONLY a JSON object in this exact format:
                        {{"emotion": "emotion_name", "confidence": float_between_0_and_1}}
                        
                        Where emotion_name is one of: {', '.join(self.emotions.keys())}
                        And confidence is your confidence level as a float between 0 and 1."""
                    },
                    {
                        "role": "user", 
                        "content": f"Classify this text: {text}"
                    }
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result)
            
        except Exception as e:
            print(f"Error calling ChatGPT API: {e}")
            return {"emotion": "error", "confidence": 0}

    def call_hf_model(self, text: str) -> Dict:
        """Call a pre-trained Hugging Face model for emotion classification."""
        try:
            result = self.hf_classifier(text)
            
            if result and isinstance(result[0], dict):
                label = result[0]['label']
                score = result[0]['score']

                # Map the Hugging Face model's label to our label set
                mapped_label = self.hf_emotion_map.get(label, 'unknown')

                return {"emotion": mapped_label, "confidence": score}
            
        except Exception as e:
            print(f"Error calling Hugging Face model: {e}")
            return {"emotion": "error", "confidence": 0}

    def load_huggingface_dataset(self, sample_size: int = 1000) -> Tuple[List[str], List[str]]:
        """Load and sample from the Hugging Face emotions dataset"""
        try:
            dataset = load_dataset("boltuix/emotions-dataset")
            train_data = dataset['train']
            print(f"Dataset column names: {train_data.column_names}")
            indices = random.sample(range(len(train_data)), min(sample_size, len(train_data)))
            texts = [train_data[i]['Sentence'] for i in indices]
            labels = [train_data[i]['Label'] for i in indices]
            return texts, labels
        except Exception as e:
            print(f"Error loading Hugging Face dataset: {e}")
            return [], []

    def evaluate_model(self, texts: List[str], true_labels: List[str], 
                             predictions: List[str], model_name: str) -> Dict:
        """Evaluate model performance"""
        valid_indices = [i for i, pred in enumerate(predictions) if pred != "error" and pred in self.emotions]
        if not valid_indices:
            return {"error": "No valid predictions"}
        
        filtered_true = [true_labels[i] for i in valid_indices]
        filtered_pred = [predictions[i] for i in valid_indices]
        
        accuracy = accuracy_score(filtered_true, filtered_pred)
        
        report = classification_report(
            filtered_true, 
            filtered_pred, 
            labels=list(self.emotions.keys()),
            target_names=list(self.emotions.keys()),
            output_dict=True,
            zero_division=0
        )
        
        return {
            "model_name": model_name,
            "accuracy": accuracy,
            "total_samples": len(filtered_true),
            "valid_predictions": len(valid_indices),
            "classification_report": report
        }

    def run_comparison(self, use_hf_dataset: bool = True, hf_sample_size: int = 200):
        """Run the complete comparison between all three approaches"""
        
        print("🚀 Starting Emotion API Comparison...")
        print("=" * 60)
        
        all_texts = []
        all_labels = []
        
        if use_hf_dataset:
            print(f"📊 Loading {hf_sample_size} samples from Hugging Face dataset...")
            hf_texts, hf_labels = self.load_huggingface_dataset(hf_sample_size)
            all_texts.extend(hf_texts)
            all_labels.extend(hf_labels)
        
        print("📝 Adding custom test samples...")
        for emotion, samples in self.test_samples.items():
            for sample in samples:
                all_texts.append(sample)
                all_labels.append(emotion)
        
        print(f"📋 Total test samples: {len(all_texts)}")
        print(f"📋 Emotion distribution: {dict(pd.Series(all_labels).value_counts())}")
        
        # Test your API
        print("\n🔧 Testing your Emotion API...")
        your_predictions = []
        your_confidences = []
        start_time_your_api = time.time()
        for i, text in enumerate(all_texts):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(all_texts)}")
            result = self.call_your_api(text)
            your_predictions.append(result.get("emotion", "error"))
            your_confidences.append(result.get("confidence", 0))
        end_time_your_api = time.time()
        print("✅ Your API testing complete.")
        your_metrics = self.evaluate_model(all_texts, all_labels, your_predictions, "Your API")
        
        # Test ChatGPT API
        print("\n🤖 Testing ChatGPT API...")
        chatgpt_predictions = []
        chatgpt_confidences = []
        start_time_chatgpt = time.time()
        for i, text in enumerate(all_texts):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(all_texts)}")
            result = self.call_chatgpt_api(text)
            chatgpt_predictions.append(result.get("emotion", "error"))
            chatgpt_confidences.append(result.get("confidence", 0))
        end_time_chatgpt = time.time()
        print("✅ ChatGPT API testing complete.")
        chatgpt_metrics = self.evaluate_model(all_texts, all_labels, chatgpt_predictions, "ChatGPT")
        
        # Test Hugging Face model
        print("\n🤗 Testing Hugging Face Model...")
        hf_model_predictions = []
        hf_model_confidences = []
        start_time_hf = time.time()
        for i, text in enumerate(all_texts):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(all_texts)}")
            result = self.call_hf_model(text)
            hf_model_predictions.append(result.get("emotion", "error"))
            hf_model_confidences.append(result.get("confidence", 0))
        end_time_hf = time.time()
        print("✅ Hugging Face model testing complete.")
        hf_model_metrics = self.evaluate_model(all_texts, all_labels, hf_model_predictions, "Hugging Face Model")
        
        # Add timing data to metrics
        your_metrics['total_time'] = end_time_your_api - start_time_your_api
        your_metrics['avg_time'] = your_metrics['total_time'] / len(all_texts)
        chatgpt_metrics['total_time'] = end_time_chatgpt - start_time_chatgpt
        chatgpt_metrics['avg_time'] = chatgpt_metrics['total_time'] / len(all_texts)
        hf_model_metrics['total_time'] = end_time_hf - start_time_hf
        hf_model_metrics['avg_time'] = hf_model_metrics['total_time'] / len(all_texts)

        # Display Results
        print("\n📊 Final Results Summary")
        print("=" * 60)
        
        self.display_summary(your_metrics, chatgpt_metrics, hf_model_metrics)
        self.display_individual_results(all_texts, all_labels, your_predictions, chatgpt_predictions, hf_model_predictions)
        self.display_confusion_matrix(all_labels, your_predictions, "Your API")
        self.display_confusion_matrix(all_labels, chatgpt_predictions, "ChatGPT")
        self.display_confusion_matrix(all_labels, hf_model_predictions, "Hugging Face Model")
        self.display_classification_report(your_metrics, chatgpt_metrics, hf_model_metrics)

    def display_summary(self, your_metrics: Dict, chatgpt_metrics: Dict, hf_model_metrics: Dict):
        """Display a summary of the key performance metrics and timing for all models."""
        print("Model Comparison Summary:")
        
        # Your API
        if "error" in your_metrics:
            print(f"  Your API: {your_metrics['error']}")
        else:
            print(f"  Your API: Accuracy = {your_metrics['accuracy']:.2f}")
            print(f"    - Valid Predictions: {your_metrics['valid_predictions']}/{your_metrics['total_samples']}")
            print(f"    - Total Time: {your_metrics['total_time']:.2f}s | Avg. per req: {your_metrics['avg_time']:.4f}s")
        
        # ChatGPT
        if "error" in chatgpt_metrics:
            print(f"  ChatGPT: {chatgpt_metrics['error']}")
        else:
            print(f"  ChatGPT: Accuracy = {chatgpt_metrics['accuracy']:.2f}")
            print(f"    - Valid Predictions: {chatgpt_metrics['valid_predictions']}/{chatgpt_metrics['total_samples']}")
            print(f"    - Total Time: {chatgpt_metrics['total_time']:.2f}s | Avg. per req: {chatgpt_metrics['avg_time']:.4f}s")
            
        # Hugging Face Model
        if "error" in hf_model_metrics:
            print(f"  Hugging Face Model: {hf_model_metrics['error']}")
        else:
            print(f"  Hugging Face Model: Accuracy = {hf_model_metrics['accuracy']:.2f}")
            print(f"    - Valid Predictions: {hf_model_metrics['valid_predictions']}/{hf_model_metrics['total_samples']}")
            print(f"    - Total Time: {hf_model_metrics['total_time']:.2f}s | Avg. per req: {hf_model_metrics['avg_time']:.4f}s")
        
        print("-" * 60)
        
    def display_individual_results(self, texts: List[str], true_labels: List[str],
                                   your_preds: List[str], chatgpt_preds: List[str], hf_preds: List[str]):
        """Display side-by-side results for a random sample of predictions."""
        print("Sample Prediction Comparison (Ground Truth vs. Your API vs. ChatGPT vs. HF Model)")
        print("-" * 60)
        
        sample_indices = random.sample(range(len(texts)), min(5, len(texts)))
        
        for i in sample_indices:
            text = texts[i]
            true_label = true_labels[i]
            your_pred = your_preds[i]
            chatgpt_pred = chatgpt_preds[i]
            hf_pred = hf_preds[i]
            
            your_match = "✅" if your_pred == true_label else "❌"
            chatgpt_match = "✅" if chatgpt_pred == true_label else "❌"
            hf_match = "✅" if hf_pred == true_label else "❌"
            
            print(f"📝 Text: {text[:100]}...")
            print(f"  - Ground Truth: {self.emotions.get(true_label, '?')} {true_label}")
            print(f"  - Your API:     {your_match} {self.emotions.get(your_pred, '?')} {your_pred}")
            print(f"  - ChatGPT:      {chatgpt_match} {self.emotions.get(chatgpt_pred, '?')} {chatgpt_pred}")
            print(f"  - HF Model:     {hf_match} {self.emotions.get(hf_pred, '?')} {hf_pred}")
            print("-" * 20)
            
    def display_confusion_matrix(self, true_labels: List[str], predictions: List[str], model_name: str):
        """Generate and display a confusion matrix heatmap."""
        
        valid_indices = [i for i, pred in enumerate(predictions) if pred in self.emotions]
        true_labels = [true_labels[i] for i in valid_indices]
        predictions = [predictions[i] for i in valid_indices]
        
        if not predictions:
            print(f"No valid predictions to generate a confusion matrix for {model_name}.")
            return
            
        cm = confusion_matrix(true_labels, predictions, labels=list(self.emotions.keys()))
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=list(self.emotions.keys()),
            yticklabels=list(self.emotions.keys())
        )
        plt.title(f"Confusion Matrix for {model_name}")
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.show()

    def display_classification_report(self, your_metrics: Dict, chatgpt_metrics: Dict, hf_model_metrics: Dict):
        """Display detailed classification reports."""
        print("\nDetailed Classification Report:")
        print("=" * 60)
        
        if "classification_report" in your_metrics:
            df = pd.DataFrame(your_metrics["classification_report"]).T
            print(f"Your API Report:")
            print(df.to_string())
            print("-" * 60)
            
        if "classification_report" in chatgpt_metrics:
            df = pd.DataFrame(chatgpt_metrics["classification_report"]).T
            print(f"ChatGPT Report:")
            print(df.to_string())
            print("-" * 60)
            
        if "classification_report" in hf_model_metrics:
            df = pd.DataFrame(hf_model_metrics["classification_report"]).T
            print(f"Hugging Face Model Report:")
            print(df.to_string())
            print("-" * 60)


def main():
    """Main function to run the comparison tool."""
    print("Emotion API Comparison Tool")
    print("=" * 40)

    # ⚙️ Configuration
    print("⚙️  Configuration:")
    your_api_url = input("Enter your Emotion API URL (default: http://localhost:8000/predict): ")
    if not your_api_url:
        your_api_url = "http://localhost:8000/predict"
    
    openai_api_key = input("Enter your OpenAI API Key: ")
    if not openai_api_key:
        print("🚨 OpenAI API Key is required to run the comparison. Exiting.")
        return

    # 🧪 Test your API connection
    print(f"\n🧪 Testing connection to your API at {your_api_url}...")
    try:
        base_url = your_api_url.rsplit('/', 1)[0]
        health_url = f"{base_url}/health"
        response = requests.get(health_url)
        
        response.raise_for_status()
        if response.status_code == 200:
            print("✅ Your API is responding correctly!")
        else:
            print(f"❌ Your API responded with status code: {response.status_code}. It might not be the correct endpoint or is not running.")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to your API: {e}. Please ensure it is running and accessible.")
        return

    # Initialize the comparator
    try:
        comparator = EmotionComparison(openai_api_key=openai_api_key, your_api_url=your_api_url)
    except Exception as e:
        print(f"❌ Failed to initialize EmotionComparison: {e}")
        return

    # Run the comparison
    comparator.run_comparison(use_hf_dataset=True, hf_sample_size=200)

if __name__ == "__main__":
    main()

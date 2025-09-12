
## 🎨 UI Components

### Main Dashboard
- **Company name input** with real-time updates
- **Speed control** with 6 TPS options
- **Start/Stop controls** for message generation
- **API status indicator** (connected/disconnected/unknown)

### Sentiment Visualization
- **Circular gauge** showing overall sentiment distribution
- **Linear progress bar** with color-coded emotions
- **Real-time updates** as new messages are processed

### Message Feed
- **Live message stream** with timestamps
- **Color-coded sentiment** (green=positive, red=negative, gray=neutral)
- **Confidence scores** for each emotion detection
- **Auto-scrolling** to show latest messages

## 🔌 API Integration

### Expected API Format

The application expects your emotion detection API to:

**Endpoint:** `POST http://localhost:8000/predict`

**Request:**
```json
{
  "text": "I am so happy today!"
}
```

**Response:**
```json
{
  "emotion": "happiness",
  "confidence": 1.0
}
```

### Supported Emotions

The app supports these emotion types:
- `happiness` (joy, excitement)
- `sadness`
- `anger`
- `fear`
- `surprise`
- `disgust`
- `love`
- `neutral`
- `confusion`
- `guilt`
- `shame`
- `desire`
- `sarcasm`

## 🚨 Troubleshooting

### Common Issues

**1. Module not found errors**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**2. CORS errors**
- Ensure your API server has CORS middleware enabled
- Check that the API is running on port 8000

**3. API connection issues**
- Verify your emotion detection API is running
- Check the API endpoint URL in the code
- Ensure the API returns the expected JSON format

**4. High CPU usage**
- Reduce the speed multiplier (lower TPS)
- Close unnecessary browser tabs
- Check for memory leaks in browser dev tools

### Performance Tips

- **For development:** Use 1x-5x speed
- **For demos:** Use 10x-20x speed
- **For stress testing:** Use 50x-100x speed
- **Monitor browser performance** with high TPS settings

## 📝 Development

### Available Scripts

```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
npm run eject      # Eject from Create React App
```

### Code Structure

- **`SocialMediaSentimentMonitor.tsx`** - Main component with all logic
- **`App.tsx`** - Root component wrapper
- **`index.tsx`** - React DOM rendering
- **`index.css`** - Global Tailwind CSS styles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Create React App](https://create-react-app.dev/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Powered by AI emotion detection
- Icons from [Heroicons](https://heroicons.com/)

---

**Happy sentiment monitoring! ��**

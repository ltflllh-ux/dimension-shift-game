// backend-server.js
// This is your backend server that will handle AI level generation
// Users will never see your API key - it stays secure on your server

const express = require('express');
const Anthropic = require('@anthropic-ai/sdk');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// IMPORTANT: Store your API key in environment variables, NEVER in code
const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY, // Set this in your environment
});

app.use(cors());
app.use(express.json());
app.use(express.static('public')); // Serve your HTML game from 'public' folder

// API endpoint for level generation
app.post('/api/generate-level', async (req, res) => {
    try {
        const { theme, level, difficulty } = req.body;

        const prompt = `You are a professional game level designer. Create a challenging and creative platformer level based on this theme: "${theme}".

Level number: ${level}
Difficulty: ${difficulty}/5

Generate a JSON response with the following structure:
{
    "platforms": [
        {"x": number, "y": number, "width": number, "height": number, "color": "hex_color"}
    ],
    "collectibles": [
        {"x": number, "y": number}
    ],
    "goalPosition": {"x": number, "y": number},
    "backgroundColor": "hex_color"
}

Requirements:
- Canvas size is 1200x800
- Create 10-20 platforms that match the theme
- Platforms should be progressively harder to reach (difficulty ${difficulty})
- Add 5-15 collectibles (coins/stars) on or near platforms
- Goal should be at the end of the level
- Use colors that match the theme
- Make platforms reachable with jumps (max vertical gap: 120px, max horizontal gap: 200px)
- Vary platform sizes (width: 60-150, height: 15-25)
- Ground should be at y=750

Be creative with platform placement to match the theme! For example:
- Pyramid shapes for Egyptian theme
- Floating platforms for space theme
- Dense foliage-like platforms for forest theme
- Neon grid patterns for cyberpunk theme`;

        const message = await anthropic.messages.create({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 4000,
            messages: [{
                role: 'user',
                content: prompt
            }]
        });

        // Extract JSON from response
        const responseText = message.content[0].text;
        const jsonMatch = responseText.match(/\{[\s\S]*\}/);
        
        if (!jsonMatch) {
            throw new Error('Could not parse level data from AI response');
        }

        const levelData = JSON.parse(jsonMatch[0]);
        
        // Validate and send response
        res.json(levelData);

    } catch (error) {
        console.error('Error generating level:', error);
        res.status(500).json({ 
            error: 'Failed to generate level',
            message: error.message 
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(PORT, () => {
    console.log(`🎮 Game server running on port ${PORT}`);
    console.log(`🔑 Make sure ANTHROPIC_API_KEY is set in environment variables`);
});

/* 
DEPLOYMENT INSTRUCTIONS:

1. Install dependencies:
   npm install express @anthropic-ai/sdk cors

2. Set your API key as environment variable:
   export ANTHROPIC_API_KEY='your-api-key-here'

3. Run the server:
   node backend-server.js

4. For production (Steam release):
   - Use a hosting service like Railway, Render, or AWS
   - Set environment variables in your hosting dashboard
   - Never commit API keys to Git
   - Use HTTPS in production
   - Consider rate limiting to control costs

5. Update the game HTML:
   Change CONFIG.API_ENDPOINT to your server URL:
   API_ENDPOINT: 'https://your-domain.com/api/generate-level'

SECURITY NOTES:
- API key stays on server, never sent to users
- Users only interact with your API endpoint
- Consider adding authentication if needed
- Monitor API usage to control costs
- Add rate limiting per user/IP
*/
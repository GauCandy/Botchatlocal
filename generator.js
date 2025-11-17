/**
 * AI Training Data Generator - Node.js Version
 * Sinh dữ liệu training chất lượng cao cho chatbot AI
 */

const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');

class TrainingDataGenerator {
    constructor(apiKey = null, apiType = 'openai', model = null) {
        this.apiKey = apiKey || process.env.OPENAI_API_KEY || process.env.ANTHROPIC_API_KEY;
        this.apiType = apiType.toLowerCase();

        // Chọn model mặc định
        if (model) {
            this.model = model;
        } else if (this.apiType === 'openai') {
            this.model = 'gpt-4o-mini';
        } else if (this.apiType === 'anthropic') {
            this.model = 'claude-3-5-haiku-20241022';
        } else {
            this.model = 'gpt-4o-mini';
        }

        this.generatedData = [];
    }

    createGenerationPrompt(scenario) {
        return `Hãy tạo một cuộc hội thoại tự nhiên giữa người dùng và AI assistant trong tình huống sau:

Chủ đề: ${scenario.topic}
Ngữ cảnh: ${scenario.context}
Mục tiêu: ${scenario.goal}
Độ dài: ${scenario.turns || 5} lượt hội thoại

Yêu cầu:
1. Cuộc hội thoại phải tự nhiên, giống cách con người nói chuyện thực tế
2. AI assistant phải hữu ích, chính xác và thân thiện
3. Bao gồm nhiều dạng câu hỏi: thông tin, hướng dẫn, giải thích, so sánh
4. Người dùng có thể hỏi follow-up questions
5. AI có thể yêu cầu làm rõ nếu câu hỏi không rõ ràng

Trả về định dạng JSON với structure:
{
    "conversation": [
        {"role": "user", "content": "câu hỏi của user"},
        {"role": "assistant", "content": "câu trả lời của AI"},
        ...
    ],
    "metadata": {
        "topic": "${scenario.topic}",
        "difficulty": "easy|medium|hard",
        "language": "vi"
    }
}

Chỉ trả về JSON, không thêm text nào khác.`;
    }

    async callOpenAI(prompt) {
        const response = await axios.post(
            'https://api.openai.com/v1/chat/completions',
            {
                model: this.model,
                messages: [
                    {
                        role: 'system',
                        content: 'Bạn là một chuyên gia tạo dữ liệu training cho AI chatbot. Bạn tạo các cuộc hội thoại chất lượng cao, tự nhiên và đa dạng.'
                    },
                    { role: 'user', content: prompt }
                ],
                temperature: 0.8,
                response_format: { type: 'json_object' }
            },
            {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                },
                timeout: 60000
            }
        );

        return response.data.choices[0].message.content;
    }

    async callAnthropic(prompt) {
        const response = await axios.post(
            'https://api.anthropic.com/v1/messages',
            {
                model: this.model,
                max_tokens: 4096,
                messages: [{ role: 'user', content: prompt }],
                system: 'Bạn là một chuyên gia tạo dữ liệu training cho AI chatbot. Bạn tạo các cuộc hội thoại chất lượng cao, tự nhiên và đa dạng. Luôn trả về JSON hợp lệ.',
                temperature: 0.8
            },
            {
                headers: {
                    'x-api-key': this.apiKey,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                timeout: 60000
            }
        );

        return response.data.content[0].text;
    }

    async generateConversation(scenario) {
        try {
            const prompt = this.createGenerationPrompt(scenario);

            let response;
            if (this.apiType === 'openai') {
                response = await this.callOpenAI(prompt);
            } else if (this.apiType === 'anthropic') {
                response = await this.callAnthropic(prompt);
            } else {
                console.log(`API type ${this.apiType} chưa được hỗ trợ`);
                return null;
            }

            // Parse response
            const data = JSON.parse(response);
            const conversationData = {
                id: `conv_${Date.now()}_${Math.floor(Math.random() * 10000)}`,
                timestamp: new Date().toISOString(),
                scenario: scenario,
                conversation: data.conversation || [],
                metadata: data.metadata || {},
                source: `${this.apiType}_${this.model}`
            };

            return conversationData;

        } catch (error) {
            console.error(`Lỗi khi sinh conversation: ${error.message}`);
            return null;
        }
    }

    async generateBatch(scenarios, batchSize = 5) {
        const conversations = [];

        // Process in batches
        for (let i = 0; i < scenarios.length; i += batchSize) {
            const batch = scenarios.slice(i, i + batchSize);
            console.log(`Đang xử lý batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(scenarios.length / batchSize)}...`);

            // Generate conversations in parallel
            const promises = batch.map(scenario => this.generateConversation(scenario));
            const results = await Promise.allSettled(promises);

            // Collect successful results
            results.forEach(result => {
                if (result.status === 'fulfilled' && result.value) {
                    conversations.push(result.value);
                    this.generatedData.push(result.value);
                }
            });

            // Small delay between batches
            if (i + batchSize < scenarios.length) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }

        return conversations;
    }

    async saveToJSON(filename, data = null) {
        data = data || this.generatedData;
        const outputDir = path.join(__dirname, 'training_data');

        // Create directory if not exists
        try {
            await fs.mkdir(outputDir, { recursive: true });
        } catch (err) {
            // Directory might already exist
        }

        const filepath = path.join(outputDir, filename);
        await fs.writeFile(filepath, JSON.stringify(data, null, 2), 'utf-8');

        console.log(`✓ Đã lưu ${data.length} conversations vào ${filepath}`);
    }

    async saveToJSONL(filename, data = null) {
        data = data || this.generatedData;
        const outputDir = path.join(__dirname, 'training_data');

        try {
            await fs.mkdir(outputDir, { recursive: true });
        } catch (err) {}

        const filepath = path.join(outputDir, filename);
        const lines = data.map(item => JSON.stringify(item)).join('\n');
        await fs.writeFile(filepath, lines, 'utf-8');

        console.log(`✓ Đã lưu ${data.length} conversations vào ${filepath}`);
    }

    async saveToOpenAIFormat(filename, data = null) {
        data = data || this.generatedData;
        const outputDir = path.join(__dirname, 'training_data');

        try {
            await fs.mkdir(outputDir, { recursive: true });
        } catch (err) {}

        const filepath = path.join(outputDir, filename);
        const lines = data.map(conv => {
            return JSON.stringify({ messages: conv.conversation });
        }).join('\n');

        await fs.writeFile(filepath, lines, 'utf-8');

        console.log(`✓ Đã lưu ${data.length} conversations vào ${filepath} (OpenAI format)`);
    }

    getStatistics(data = null) {
        data = data || this.generatedData;

        if (!data || data.length === 0) {
            return { total_conversations: 0 };
        }

        const totalTurns = data.reduce((sum, conv) => sum + conv.conversation.length, 0);
        const topics = {};

        data.forEach(conv => {
            const topic = conv.scenario.topic;
            topics[topic] = (topics[topic] || 0) + 1;
        });

        return {
            total_conversations: data.length,
            total_turns: totalTurns,
            avg_turns_per_conversation: totalTurns / data.length,
            topics_distribution: topics,
            date_generated: new Date().toISOString()
        };
    }
}

// Vietnamese scenarios
const VIETNAMESE_SCENARIOS = [
    {
        topic: 'Lập trình Python cơ bản',
        context: 'Người dùng muốn học Python',
        goal: 'Giải thích cách bắt đầu học Python',
        turns: 6
    },
    {
        topic: 'Machine Learning cơ bản',
        context: 'Người dùng muốn hiểu về AI/ML',
        goal: 'Giải thích khái niệm ML đơn giản',
        turns: 7
    },
    {
        topic: 'Nấu ăn món Việt',
        context: 'Người dùng muốn học nấu món truyền thống',
        goal: 'Hướng dẫn công thức nấu ăn',
        turns: 7
    },
    {
        topic: 'Du lịch Việt Nam',
        context: 'Người dùng lên kế hoạch du lịch',
        goal: 'Tư vấn địa điểm và lịch trình',
        turns: 8
    },
    {
        topic: 'Học tiếng Anh',
        context: 'Người dùng muốn cải thiện tiếng Anh',
        goal: 'Tư vấn phương pháp học hiệu quả',
        turns: 6
    },
    {
        topic: 'Khởi nghiệp kinh doanh',
        context: 'Người dùng muốn mở doanh nghiệp',
        goal: 'Tư vấn các bước khởi nghiệp',
        turns: 8
    },
    {
        topic: 'Marketing online',
        context: 'Người dùng muốn quảng cáo sản phẩm',
        goal: 'Hướng dẫn chiến lược marketing',
        turns: 7
    },
    {
        topic: 'Nhiếp ảnh di động',
        context: 'Người dùng muốn chụp ảnh đẹp bằng điện thoại',
        goal: 'Hướng dẫn kỹ thuật chụp ảnh',
        turns: 6
    },
    {
        topic: 'Quản lý tài chính cá nhân',
        context: 'Người dùng muốn tiết kiệm tiền',
        goal: 'Tư vấn cách quản lý chi tiêu',
        turns: 7
    },
    {
        topic: 'Web Development',
        context: 'Người dùng muốn tạo website',
        goal: 'Hướng dẫn công nghệ web cần học',
        turns: 6
    }
];

async function main() {
    console.log('='.repeat(60));
    console.log('AI TRAINING DATA GENERATOR (Node.js)');
    console.log('Sinh dữ liệu training chất lượng cao cho chatbot');
    console.log('='.repeat(60));
    console.log();

    // Check API key
    const apiKey = process.env.OPENAI_API_KEY || process.env.ANTHROPIC_API_KEY;

    if (!apiKey) {
        console.log('⚠ Cảnh báo: Không tìm thấy API key!');
        console.log('Vui lòng set environment variable:');
        console.log('  export OPENAI_API_KEY=\'your-key-here\'');
        console.log('  hoặc');
        console.log('  export ANTHROPIC_API_KEY=\'your-key-here\'');
        return;
    }

    // Determine API type
    const apiType = process.env.OPENAI_API_KEY ? 'openai' : 'anthropic';
    console.log(`✓ Sử dụng ${apiType.toUpperCase()} API`);

    // Initialize generator
    const generator = new TrainingDataGenerator(apiKey, apiType);
    console.log(`✓ Model: ${generator.model}`);
    console.log(`✓ Số scenarios: ${VIETNAMESE_SCENARIOS.length}`);
    console.log();

    // Generate data
    console.log('Đang sinh dữ liệu training...');
    console.log('(Quá trình này có thể mất vài phút)');
    console.log();

    const conversations = await generator.generateBatch(VIETNAMESE_SCENARIOS, 5);

    console.log();
    console.log('='.repeat(60));
    console.log(`✓ Đã sinh ${conversations.length} conversations thành công!`);
    console.log('='.repeat(60));
    console.log();

    // Save data
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];

    await generator.saveToJSON(`conversations_${timestamp}.json`);
    await generator.saveToJSONL(`conversations_${timestamp}.jsonl`);
    await generator.saveToOpenAIFormat(`openai_format_${timestamp}.jsonl`);

    // Show statistics
    console.log();
    console.log('='.repeat(60));
    console.log('THỐNG KÊ');
    console.log('='.repeat(60));

    const stats = generator.getStatistics();
    console.log(`Tổng số conversations: ${stats.total_conversations}`);
    console.log(`Tổng số turns: ${stats.total_turns}`);
    console.log(`Trung bình turns/conversation: ${stats.avg_turns_per_conversation.toFixed(1)}`);
    console.log();
    console.log('Phân bố theo chủ đề:');

    const sortedTopics = Object.entries(stats.topics_distribution)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    sortedTopics.forEach(([topic, count]) => {
        console.log(`  • ${topic}: ${count} conversations`);
    });

    console.log();
    console.log('='.repeat(60));
    console.log('✓ HOÀN THÀNH!');
    console.log('='.repeat(60));
    console.log();
    console.log('Dữ liệu đã được lưu trong thư mục: training_data/');
    console.log('Bạn có thể dùng các file này để train chatbot của mình!');
}

// Run if this is the main module
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { TrainingDataGenerator, VIETNAMESE_SCENARIOS };

#!/usr/bin/env node

const crypto = require('crypto');
const readline = require('readline');

// --- Configuration ---
const DECK_SIZE = 78;
// WARNING: 888888 iterations is computationally expensive and will be slow in JS.
const THINK_DEPTH = 888888; 

// --- Tarot Card List ---
const cards = [
    'The Fool', 'The Magician', 'The High Priestess', 'The Empress', 'The Emperor', 'The Hierophant',
    'The Lovers', 'The Chariot', 'Strength', 'The Hermit', 'Wheel of Fortune', 'Justice', 'The Hanged Man',
    'Death', 'Temperance', 'The Devil', 'The Tower', 'The Star', 'The Moon', 'The Sun', 'Judgment', 'The World',
    'Ace of Wands', 'Two of Wands', 'Three of Wands', 'Four of Wands', 'Five of Wands', 'Six of Wands',
    'Seven of Wands', 'Eight of Wands', 'Nine of Wands', 'Ten of Wands', 'Page of Wands', 'Knight of Wands',
    'Queen of Wands', 'King of Wands', 'Ace of Cups', 'Two of Cups', 'Three of Cups', 'Four of Cups',
    'Five of Cups', 'Six of Cups', 'Seven of Cups', 'Eight of Cups', 'Nine of Cups', 'Ten of Cups',
    'Page of Cups', 'Knight of Cups', 'Queen of Cups', 'King of Cups', 'Ace of Swords', 'Two of Swords',
    'Three of Swords', 'Four of Swords', 'Five of Swords', 'Six of Swords', 'Seven of Swords', 'Eight of Swords',
    'Nine of Swords', 'Ten of Swords', 'Page of Swords', 'Knight of Swords', 'Queen of Swords', 'King of Swords',
    'Ace of Pentacles', 'Two of Pentacles', 'Three of Pentacles', 'Four of Pentacles', 'Five of Pentacles',
    'Six of Pentacles', 'Seven of Pentacles', 'Eight of Pentacles', 'Nine of Pentacles', 'Ten of Pentacles',
    'Page of Pentacles', 'Knight of Pentacles', 'Queen of Pentacles', 'King of Pentacles'
];

/**
 * Hashes a question string multiple times to generate a large number.
 * @param {string} question The input string.
 * @param {string} salt A salt to append to the string.
 * @param {number} times The number of times to hash.
 * @returns {bigint} A large integer derived from the final hash.
 */
function hashQuestion(question, salt = "", times = THINK_DEPTH) {
    let h = Buffer.from(question + salt);
    for (let i = 0; i < times; i++) {
        h = crypto.createHash('sha512').update(h).digest();
    }
    // Convert the buffer to a BigInt, similar to Python's int.from_bytes
    return BigInt('0x' + h.toString('hex'));
}

/**
 * Draws a specified number of unique cards from the deck.
 * @param {string} question The user's question, used as a seed.
 * @param {number} count The number of cards to draw.
 * @returns {string[]} An array of drawn card names.
 */
function drawCards(question, count) {
    const drawn = [];
    const usedIndices = new Set();
    const timestamp = Math.floor(Date.now() / 1000); // Time-based randomness

    for (let i = 0; i < count; i++) {
        let rehashCounter = 0;
        while (true) {
            // Create a unique salt for each card draw attempt
            const salt = `${question}-card${i}-time${timestamp}-retry${rehashCounter}`;
            // The result of a BigInt modulo a Number is a BigInt, so we convert to Number
            const index = Number(hashQuestion(question, salt) % BigInt(DECK_SIZE));
            
            if (!usedIndices.has(index)) {
                usedIndices.add(index);
                drawn.push(cards[index]);
                break;
            }
            rehashCounter++;
        }
    }
    return drawn;
}

// --- Main Logic ---
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Helper to ask questions using promises
const questionAsync = (prompt) => new Promise(resolve => rl.question(prompt, resolve));

async function main() {
    console.log("Welcome to Node.js Tarot");
    const question = await questionAsync("Ask your sacred question: ");

    console.log("\nChoose your spread:");
    console.log("1: Single Card");
    console.log("3: Three Card Spread (Past, Present, Future)");
    console.log("10: Celtic Cross");
    const spreadChoice = await questionAsync("Your choice (1/3/10): ");

    let spread = parseInt(spreadChoice.trim(), 10);
    if (isNaN(spread) || ![1, 3, 10].includes(spread)) {
        console.log("\nInvalid choice. Defaulting to 1 card.");
        spread = 1;
    }

    //console.log("\nDrawing your cards... (this may take a moment)");
    const drawnCards = drawCards(question, spread);

    console.log(`\nYour Card${spread > 1 ? 's' : ''}:`);

    if (spread === 10) {
        const celticPositions = [
            "1. Present", "2. Challenge", "3. Past Influences", "4. Future Possibilities",
            "5. Above (Conscious Focus)", "6. Below (Subconscious Influence)",
            "7. Advice", "8. External Influences", "9. Hopes and Fears", "10. Outcome"
        ];
        drawnCards.forEach((card, i) => {
            console.log(`${celticPositions[i]}: ${card}`);
        });
    } else {
        drawnCards.forEach((card, i) => {
            console.log(`${i + 1}. ${card}`);
        });
    }

    rl.close();
}

main().catch(err => {
    console.error("An error occurred:", err);
    rl.close();
});

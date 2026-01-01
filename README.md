# Repeater Divination
The Intention Repeater Tarot by Thomas Sweet/AnthroHeart (https://intentionrepeater.boards.net; https://github.com/tsweet77/openrouter-tarot) was translated by Gemini CLI (Pro 2.5) into Runes, Astrology, Kabbalah and probably others to come. Enjoy!

# EngWheelSuited.html is the ultimate version.

December 10: You can read commits and code for details. Aastrology.py was updated with os.urandom() and SHA256-PBKDF2-HMAC, the minor bodies have also been gated with a commandline switch/option. Only the top 20 Aspects/Transits are shown by default, but you can change that number. A couple tools have warned that ASTROLOGY.py is faulty and must not be used. 2IngWheel.py is IngWheel.html but adapted for commandline Python (better than early experiments). You select numbers by writing them. KABBALAH5.py is a transition version. KABBALAH6.py has been described as reliable. Excessive/Deficient Sephiroth ratio was dropped to 7.5%/7.5%.<br><br>
However, KABBALAH7.py is more reliable than it, as it has been updated to use a fluid dynamics model, where the Paths are liquid tubes connecting the Sephiroth by how much inflow and outflow they have.<br><br>
KABBALAH7.py's inflow/outflow system is tinted (shifted) by one of the 4 worlds, plus the 5th default world that doesn't shift it. K7 also has Da'at (Knowledge), the "hidden" Sephirah.

All old remaining versions have been moved to the Historical folder.

An astrology reading can be so much data that one AI can answer "Yes", but a second AI can answer "No". Therefore I do not really like it anymore. December 25 Update: though Aastrology.py tends to be accurate

September 24: divination.html was an 1 file Divination system that combines Tarot, I Ching, Kabbalah and Runes. DIVINATION.py is its older Python version.<br>
DivinationColors.html was the v2, with a grid of numbers. DivinationColors2.html includes an automated button.<br>
DivinationColors3.html is the newest version with < > buttons for going back and forth on automated draws.<br>
DivinationToolAdvanced.html includes Dreamspell and Taixuanjing, a Chinese divination book, similar to IChing, but with 81 tetragrams.<br>
DivinationAdvancedTool2.html includes Lingqinjing.<br>

DivinationAdvancedTool3.html includes Astrology, Ogham, and Meihua Yishu, as well as removing the number grid. This is the ultimate version.

August 22 Update: `tarot_reader.py` was made by 4.1 Opus and uses SHA256-PBKDF2-HMAC rather than plain SHA512. `"The formula is essentially HMAC(password, salt + iteration_count)"` which is richer for free compared to the older methods. It also supports piped input, does reversals and "verifies its output".

All older files are obsolete and will be upgraded with the new mechanisms soon.

TAROT.py was further beautified/cleaned up by GPT5. AnthroHeart/@Anthro really likes it.<br>
TAROT2.py makes it automatic as I-CHING3.py.

I-CHING2.py was "Ok, made an update so that it always displays text in the Image, and it keeps up the animation message until drawn." December 25 update (actually earlier): I-CHING3.py had a trigram reversal bug which was fixed. The style of I-CHING2.py was deemed as less info-rich, so it was stashed in Historical.

KABBALAH3.py was made "automatic" like I-CHING3.py is. You can choose to use it or not.<br>
KABBALAH4.py becomes like I-CHING3.py: varying results by timestamp.

Likewise for RUNES.py.

---

Symmetrical runes (that look the same any side) such as Gebo do not traditionally have a reversed form. Despite this, recent tool versions do include their reversed forms.

cio.py is a non-interactive experiment in generating hashed readings from the AnthroHeart Cio Saga.

The Tarot file once was GPL3, and since all the other files were derived from it, they were too. However, as of December 2025, AnthroHeart/Cio has moved to CC0 for everything he makes, so I have too.

Geomancy's 15 "drawables" felt too slanted to negativity, and I-CHING3.py recommended me to delete it, so I did.

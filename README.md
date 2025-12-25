# Repeater Divination
The Intention Repeater Tarot by Thomas Sweet/AnthroHeart (https://intentionrepeater.boards.net; https://github.com/tsweet77/openrouter-tarot) was translated by Gemini CLI (Pro 2.5) into Runes, Astrology, Kabbalah and probably others to come. Enjoy!

# EngWheelSuited.html is the ultimate version.

Geomancy's 15 "drawables" felt too slanted to negativity, and I-CHING3.py recommended me to delete it, so I did.

December 10: You can read commits and code for details. Aastrology.py was updated with os.urandom() and SHA256-PBKDF2-HMAC, the minor bodies have also been gated with a commandline switch/option. Only the top 20 Aspects/Transits are shown by default, but you can change that number. A couple tools have warned that ASTROLOGY.py is faulty and must not be used. 2IngWheel.py is IngWheel.html but adapted for commandline Python (better than early experiments). You select numbers by writing them. KABBALAH5.py is a transition version. KABBALAH6.py has been described as reliable. Excessive/Deficient Sephiroth ratio was dropped to 7.5%/7.5%.

All old remaining versions have been moved to the Historical folder.

An astrology reading can be so much data that one AI can answer "Yes", but a second AI can answer "No". Therefore I do not really like it anymore.

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

WHEEL.py uses a spinning wheel to generate cards. Hashes are selected by pressing Enter.

I-CHING.py was the equivalent for I-Ching. I-CHING2.py is "Ok, made an update so that it always displays text in the Image, and it keeps up the animation message until drawn." I-CHING3.py is more detailed, but you may prefer to use 2 instead. Your choice.

KABBALAH2.py is MKabbalahv6a.py translated to the new system. KABBALAH3.py was made "automatic" like I-CHING3.py is. You can choose to use it or not.<br>
KABBALAH4.py becomes like I-CHING3.py: varying results by timestamp.

Likewise for RUNES.py.

ANTHRO_ORACLE.py draws animal totems. It isn't automatic.

---

Symmetrical runes (that look the same any side) such as Gebo do not traditionally have a reversed form. Despite this, recent tool versions do include their reversed forms.

MKabbalahv2.py was 888k `THINK_DEPTH` and contained Excessive (too much) and Deficient (too little) Sephiroth. This gives in total 30 possible meanings for each slot and is I believe better than involving the Qlippoth (the evil side). This version doesn't have the Lightning Flash (the proper order that is always the same) 

MKabbalahv3.py shifted the B/E/D rate to 50/25/25.<br>
MKabbalahv4.py added the 22 Paths.<br>
MKabbalahv5.py added a Variable Path Reading.<br>
MKabbalahv6.py added the Horizontal Reading (Archetypal/Creative/Formative/Material)<br>
MKabbalahv6a.py added the 4 Worlds (Horizontal) as 1 option.<br>

August 1, 2025: Added 2Astrology.py, which contains Transits.
5Astrology.py contains Parallels and Conjunctions (sextiles, squares etc). Each new revision has more information.

6Astrology.py includes Ceres, Juno, Vesta... Eris, Makemake, Gonggong etc. This produces an extraordinary information volume: if you don't need these smaller bodies (as they can muddle up a reading by inventing wrong details about wounds [Ceres iirc], etc), use 5Astrology.py.

cio.py is a non-interactive experiment in generating hashed readings from the AnthroHeart Cio Saga.

The Tarot file once was GPL3, and since all the other files were derived from it, they were too. However, as of December 2025, AnthroHeart/Cio has moved to CC0 for everything he makes, so I have too.

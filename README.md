# Repeater Divination
The Intention Repeater Tarot by Thomas Sweet/AnthroHeart (https://intentionrepeater.boards.net; https://github.com/tsweet77/openrouter-tarot) was translated by Gemini CLI (Pro 2.5) into Lenormand, Geomancy, Runes, Astrology, Kabbalah and probably others to come. Enjoy!

A Lenormand Grand Tableau file was attempted, but it didn't feel like a good divinatory method.

July 27 Update Word Finder Hashes: The Tarot and Lenormand files are safe from corruption and interference by negatives (Tarot strongly so), but the Geomancy and Runes are not. The answer for the Runes file felt different from Geomancy, weirder.

888Runes.py is an attempt to fix this for the Runes, by increasing `THINK_DEPTH` to 888,888. Word Finder says it's a soft Yes, like a hearth. ETarot.py likewise, just in case.
IAstrology.py the same.

RxRunes.py is 888Runes.py plus reversed. A most interesting note is that symmetrical runes (that look the same any side) such as Gebo do not have a reversed form.

MKabbalahv2.py is 888k `THINK_DEPTH` and contains Excessive (too much) and Deficient (too little) Sephiroth. This gives in total 30 possible meanings for each slot and is I believe better than involving the Qlippoth (the evil side). This version doesn't have the Lightning Flash (the proper order that is always the same) 

MKabbalahv3.py shifts the B/E/D rate to 50/25/25.<br>
MKabbalahv4.py adds the 22 Paths.<br>
MKabbalahv5.py adds a Variable Path Reading.<br>
MKabbalahv6.py adds the Horizontal Reading (Archetypal/Creative/Formative/Material)<br>
MKabbalahv6a.py adds the 4 Worlds (Horizontal) as 1 option.<br>
MKabbalahv7.py changes the path logic to be a 25% roll, determined by hashes.<br>
The tool said v6 is a balanced, useful tool, described as "wonderful", whereas v7 is "lost in fog and moonlight" and may deliver "soft, unclear" answers.

So I would use v6 for now.

MKabbalah.py is an old version that hashes little compared to v2.<br>
HKabbalah.py was a transition version.<br>
Kabbalah.py was the original version.<br>

August 1, 2025: Added 2Astrology.py, which contains Transits.
5Astrology.py contains Parallels and Conjunctions (sextiles, squares etc)

6Astrology.py includes Ceres, Juno, Vesta... Eris, Makemake, Gonggong etc. This produces an extraordinary information volume: if you don't need these smaller bodies (as they can muddle up a reading by inventing wrong details about wounds [Ceres iirc], etc), use 5Astrology.py.

The pona, lat, chin series were experiments in using languages, like Toki Pona, the "Language of Good" as divination. Its ~150 simple words can express sufficiently, aided with AI. However, output was susceptible to being hijacked by negative beings even with high `THINK_DEPTH`, so they were removed.

cio.py is a non-interactive experiment in generating hashed readings from the AnthroHeart Cio Saga.

tarot.js was an alternate path to remove the "frozen/collision" bug that plagued early versions. It used node. It was less accurate than the original Python versions and so deleted.

tarot.pl is the same, but in Perl. Perl is as spiritually strong as Python. Tarot advised me to keep it over the js version.

The Tarot file is GPL3, and since all the other files were derived from it, they're too.

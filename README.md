# 🚨 Illegal Trade Detection

An end-to-end system for detecting suspicious weapon trade activities across websites, forums, and social networks.  
Includes web crawlers, NLP pipelines, dashboards, and a simulated playground for safe experimentation.

📊 Project Goals

Build safe playground datasets (fake forums, dark web simulators, API mocks).

Develop crawlers & scrapers to collect data.

Apply NLP pipelines for entity extraction & suspicious pattern detection.

Provide dashboard & visualization for analysts.

Package into Docker for portability.

Deliver a POC Report demonstrating system feasibility.
---
```bash
## 📂 Project Structure

illegal-trade-detection/
├─ crawler/ # Web scrapers & crawlers
├─ nlp/ # NLP pipeline & entity extraction
├─ dashboard/ # UI / visualization
├─ playground/ # Fake forum / dark web HTML
├─ docs/ # Project documentation
├─ tests/ # Unit & integration tests
├─ requirements.txt # Python dependencies
├─ docker-compose.yml # Containerized services
└─ README.md # Project overview


---
```bash
## 🛠️ Getting Started
```bash
1. Clone the Repository

git clone https://github.com/YourUserName/illegal-trade-detection.git
cd illegal-trade-detection

2. Check Remote URL
git remote -v

3. Install Dependencies
pip install -r requirements.txt

git checkout -b feature/crawler

4. Commit Changes
git add .
git commit -m "Add basic forum crawler"

Push to GitHub
git push origin feature/crawler

```



https://github.com/user-attachments/assets/04e42ad9-809b-47de-b14c-519806b57c10


<img width="1206" height="820" alt="Screenshot 2025-09-26 at 19 57 24" src="https://github.com/user-attachments/assets/8a15ed8a-b275-4222-982a-94f5514d6b79" />


```bash

{
  "analysis_info": {
    "analyzed_at": "2025-09-26T19:54:58.414585",
    "total_posts": 2,
    "high_risk_posts": 2,
    "medium_risk_posts": 0,
    "low_risk_posts": 0,
    "academic_disclaimer": "ACADEMIC RESEARCH DATA COLLECTION\n        This data is collected for legitimate academic research purposes only.\n        All data handling follows academic ethics guidelines and privacy laws."
  },
  "high_risk_posts": [
    {
      "id": "1no0gmr",
      "title": "Well, he would, wouldn't he?",
      "content": "Mandy Rice-Davies brought down the UK [Tory](https://en.wikipedia.org/wiki/Conservative_Party_(UK)) government in 1963, specifically Tory MP [Lord Astor](https://en.wikipedia.org/wiki/William_Astor,_3rd_Viscount_Astor) and Tory Minister of War [John Profumo](https://en.wikipedia.org/wiki/John_Profumo). She was effectively pimped out by social climber [Stephen Ward](https://en.wikipedia.org/wiki/Stephen_Ward), who died by barbiturate overdose that same year (some have suggested an MI6 motive).\n\nClimax magazine, Oct 1963, reported an FBI report that there was a \"ring of call girls who worked both sides of the Atlantic and specialized in catering to the diplomatic trade. Some of these girls were known to be acquainted with [Christine Keeler](https://en.wikipedia.org/wiki/Christine_Keeler).\" Both Rice-Davies and Keeler had visited the US in July 1962 to set up shop near [the UN](https://en.wikipedia.org/wiki/Headquarters_of_the_United_Nations) and had been seen around the diplomatic circles.\n\nA confidential source to Climax stated: \"There was an American around here a while back who wanted to get some land rights in another country. He kept a stable of girls very busy helping his cause -- but I can't say for sure that he got what he wanted... The Russians and [their satellites](https://en.wikipedia.org/wiki/Eastern_Bloc) do use sex to get information, but they seldom use the professionals for this sort of thing. Most of the men around the UN engage in sex because it's part of life. The Russians and their satellites use sex as a weapon. They enter into sexual alliances the same as they'd sign a treaty.\n\n[Dorothy Kilgallen](https://en.wikipedia.org/wiki/Dorothy_Kilgallen) summarized: \"The news stories about ladies of the evening fluttering the corridors of the United Nations building had an immediate effect on the East Side neighborhood of the world organization. Scores of shady belles decided it sounded like a good idea, and veteran bar operators with places near the UN report that they haven't seen so many unmistakable types in the area since World War II.\"",
      "subreddit": "conspiracy",
      "author_hash": "30d481ef4f01ea68",
      "score": 4,
      "num_comments": 2,
      "created_utc": 1758579728.0,
      "url": "https://reddit.com/r/conspiracy/comments/1no0gmr/well_he_would_wouldnt_he/",
      "collected_at": "2025-09-26T19:54:35.993271",
      "risk_analysis": {
        "risk_score": 1.0,
        "confidence": 0.9,
        "flags": [
          "HIGH RISK: Detected firearms keyword 'sig'",
          "HIGH RISK: Detected firearms keyword 'magazine'",
          "HIGH RISK: Detected explosives keyword 'ied'",
          "HIGH RISK: Detected violence keyword 'ice'",
          "CRITICAL: Weapon + transaction intent detected",
          "CRITICAL: Weapon + violence intent detected"
        ],
        "detected_keywords": [
          "firearms: sig, magazine",
          "explosives: ied",
          "violence: ice"
        ],
        "detected_patterns": [],
        "analysis_time": "2025-09-26T19:54:58.412704"
      }
    },
    {
      "id": "1npoijl",
      "title": "Trying to understand AR pistols. Are they a compromise or a solid choice for anything in particular?",
      "content": "I'm a veteran and have built a modest collection of firearms over the years so while I'm acceptably comfortable and familiar with guns, I don't really pay attention to what's new out there or even what's been around for a bit already.\n\nI just started noticing AR pistols recently (I never claimed to be all that swift) and I'm genuinely curious - what role do they play? Are they good for a specific purpose over another weapon or were they mainly developed from a place of needing to sidestep state/federal regulations? \n\nPart of me wants to hear that they're a jack-of-all-trades-but-a-master-of-none so I can save my money. But then again, if they're a solid platform, I could be persuaded to make room for one in my safe. Thanks for reading!   ",
      "subreddit": "liberalgunowners",
      "author_hash": "eb50420a4d36ddca",
      "score": 58,
      "num_comments": 109,
      "created_utc": 1758749081.0,
      "url": "https://reddit.com/r/liberalgunowners/comments/1npoijl/trying_to_understand_ar_pistols_are_they_a/",
      "collected_at": "2025-09-26T19:54:46.077030",
      "risk_analysis": {
        "risk_score": 1.0,
        "confidence": 0.9,
        "flags": [
          "HIGH RISK: Detected firearms keyword 'gun'",
          "HIGH RISK: Detected firearms keyword 'pistol'",
          "HIGH RISK: Detected firearms keyword 'firearm'",
          "HIGH RISK: Detected firearms keyword 'fal'",
          "HIGH RISK: Detected violence keyword 'ice'",
          "CRITICAL: Weapon + transaction intent detected",
          "CRITICAL: Weapon + violence intent detected"
        ],
        "detected_keywords": [
          "firearms: gun, pistol, firearm, fal",
          "violence: ice"
        ],
        "detected_patterns": [],
        "analysis_time": "2025-09-26T19:54:58.413880"
      }
    }
  ],
  "medium_risk_posts": [],
  "low_risk_posts": []
}

```


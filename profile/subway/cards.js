// past-project cards. facts are from the owner's resume and repo READMEs, lowercased; the jobradar alerts are from a real
// local scan (profile/data/jobradar-scan.json) and the sportsgrid messages are the bot's own text. name and colour come
// from data.js. no commit counts or dates here: the cards are rendered once, the lanes and map carry the live numbers.
window.CARDS = {
  'jobradar-ai': { secs: 7, demo: 'alerts',
    what: 'my personal internship radar. it scouts github internship lists around the clock and pings my phone when something new shows up.',
    note: 'a scan on nov 11 found 835 listings that fit my filters. 9 were at companies on my priority list, and those ping first.',
    steps: ['scout github internship lists', 'drop duplicates', 'classify the role', 'store in sqlite', 'push to phone, discord or telegram'],
    stack: ['python', 'sqlite', 'github actions'],
    // profile/data/jobradar-scan.json, first three alerts, in the bot's own format
    scan: { scanned: 'nov 11', alerts: [
      ['NVIDIA', 'AI Systems Software Engineering Intern – Summer 2027 | Austin, TX'],
      ['Palantir', 'Software Engineer, Intern - Connectivity Platform and Product | New York, NY'],
      ['Metamorphic', 'Research and Engineering Intern (Summer 2027) | Palo Alto, CA']] } },
  'dailygames-slackbot': { secs: 7, demo: 'slack',
    what: "a slack bot that posts the day's puzzle threads and keeps a leaderboard per channel.",
    note: 'about 120 people play in it, roughly 4,000 messages a month.',
    steps: ['wordle, connections, statpad, immaculate grid', 'one thread per game, every morning', 'reads scores from replies', 'per-channel leaderboards', 'five-command cli setup'],
    stack: ['node.js', 'slack bolt', 'railway'] },
  'kalshi-ev-extension': { secs: 6,
    what: 'a chrome extension that floats an expected-value widget on kalshi sports markets, priced against sportsbook odds.',
    note: 'the widget loads in 50 ms, down from 2 s, by caching live games in the service worker.',
    steps: ['open any kalshi sports market', 'match it to the game, fuzzy if needed', 'pull consensus sportsbook odds', 'show yes / no expected value', 'estimate profit after fees'],
    stack: ['javascript', 'chrome mv3', 'odds api'] },
  'neetcode-submissions': { secs: 6,
    what: 'interview practice, synced straight from neetcode so every attempt is versioned.',
    steps: ['solve on neetcode', 'each submission syncs here', 'retries kept side by side'],
    stack: ['python'] },
  'evision': { secs: 6,
    what: 'the web-app version of kalshi ev: scans markets against sportsbook odds and surfaces positive-ev bets.',
    steps: ['pull kalshi markets and sportsbook lines', 'remove the vig', 'compute edge', 'size bets with the kelly criterion', 'show opportunities with 2%+ edge'],
    stack: ['python', 'fastapi', 'postgresql', 'google oauth'] },
  'rohan_drone_club': { secs: 7.4, demo: 'drone', frames: 80,
    what: 'turns a drone flight video into one panorama of the whole path.',
    note: 'the panorama here is what its stitcher made from four frames of the test flight, in 1.1 s.',
    steps: ['pull frames at a smart interval', 'downsample for speed', 'stitch with opencv'],
    stack: ['python', 'opencv'] },
};

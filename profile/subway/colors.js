// The colouring guide. One place for every line colour; pages read it through lib.js (colours()).
//   now     building now: the brightest colours. a line whose lane opens its film (link "film") is in this tier
//   side    side projects on the map: mid-saturation
//   work    past work (jobs): muted
//   retired past projects that dropped off the map: one grey
// "pinned" fixes a colour to a key for good. A new project takes a colour from its tier's "spare" list by a hash of its key,
// skipping colours already in use, so it gets the same colour every day without anyone choosing it.
window.PALETTE = {
  now:  { pinned: { 'vel': '#ffc400', 'lea': '#f0528f' }, spare: ['#ff7d4d', '#3ad0e0', '#b6e038', '#ff8fd0'] },
  side: { pinned: { 'jobradar-ai': '#1faa5e', 'dailygames-slackbot': '#3b82f0', 'neetcode-submissions': '#ff6a2b',
                    'kalshi-ev-extension': '#35c2d1', 'evision': '#a06be6', 'rohan_drone_club': '#8b8e92' },
          spare: ['#c9543f', '#7da33a', '#5b6ee8', '#12a08e', '#b0791f', '#c06aa8', '#4f9bd6', '#9a8a5a'] },
  work: { pinned: { 'climate-plans': '#7fa58c', 'ariento': '#8d9bc4' }, spare: ['#b09a78', '#a58aa8', '#86a3a8', '#a8a27a'] },
  retired: '#74777b',
};

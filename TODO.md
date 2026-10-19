# To-do

## Next up

### Real water (GPU water simulation)

Replace the drawn ripple rings with a real water surface, so ripples bend everything under them.

- [ ] Height-field wave simulation on the GPU (WebGL), at a lower resolution than the screen for speed
- [ ] Draw the scene (koi, pads, lotus, frog, boats) first, then view it through the water so ripples refract it
- [ ] Caustics: moving light patterns on the pond floor, strongest at midday, gone at night
- [ ] Waves that interfere when they cross and reflect softly off the pond edges
- [ ] Glints on wave crests in the time-of-day light colour (sun, sunset, moon)
- [ ] Wakes from koi, the paper boat, the frog landing and the dragonfly dipping
- [ ] Rain makes the whole surface shimmer
- [ ] Automatic fallback to the current 2D canvas drawing when WebGL is not available
- [ ] Calmer, lighter simulation in sleep mode (battery) and gentler distortion with reduced motion
- [ ] Test on low-power phones, all times of day, rain, every mode, and the fallback

## Ideas

### Rare magical moments
- [ ] Golden koi that appears very rarely and glows faintly; feeding it plays a special chime
- [ ] Shooting star reflected across the night water
- [ ] Rainbow after the rain stops
- [ ] Full moon nights on real full-moon dates: bigger moon, lotus flowers open and glow
- [ ] Lantern nights: paper lanterns drift across by themselves

### Seasons (from the real date)
- [ ] Spring: cherry blossom petals drift down and float
- [ ] Monsoon: more rain, more frogs, louder chorus
- [ ] Autumn: orange leaves fall and spin in the ripples
- [ ] Cool season: longer morning mist, steam rising at dawn

### Your pond grows
- [ ] Something small appears each day you visit (stone lantern, bridge, new koi, reeds, fountain)
- [ ] Tap and hold a koi to give it a name

### Shared pond
- [ ] Paper boats from Let go float in a pond shared by everyone who opens the link, with the words hidden
- [ ] Needs shared storage; check what the hosting option supports

### Music
- [ ] Optional soft ambient music bed that evolves slowly and stays in harmony with your taps

## Done

- [x] Pond with ripples and pentatonic notes; hold for a big stone; drag for a trail
- [x] Koi that wander and gather at taps; lily pads that bob; lotus flowers
- [x] Day and night from the local clock (morning mist, sunset, moon, stars, fireflies)
- [x] Rain with ripples, notes and sound
- [x] Four sound styles, volume controls, nature sounds (water, birds, crickets)
- [x] Breathe with the Pond (guided lotus breathing, 1/3/5 minutes, real-time clock)
- [x] Let go (paper boat carries a written worry away; nothing saved)
- [x] Frog: hops, blinks, croaks, catches fireflies at night
- [x] Feed the koi
- [x] Daytime dragonfly; distant frog chorus at night and in rain
- [x] Sleep mode with 15/30/60 minute timer, dimming, sound fade and screen wake lock

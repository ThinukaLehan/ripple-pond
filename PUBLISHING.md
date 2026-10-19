# Publishing Ripple Pond

| Where | Status | Cost |
| --- | --- | --- |
| Website (GitHub Pages) | **Live:** https://thinukalehan.github.io/ripple-pond/ | Free |
| Installable app (Add to Home Screen) | **Live:** works from the website on phones and computers | Free |
| itch.io | Ready to upload: `release/ripple-pond-itch.zip` | Free |
| Microsoft Store | Ready to package with PWABuilder | Free for individual developers |
| Google Play | Ready to package with PWABuilder; needs a 14-day closed test with 12 testers first | $25 once |
| Apple App Store | Later (needs a Mac and $99/year; Apple often rejects simple web wrappers) | $99/year |

Everything the stores ask for is in this repo:

- **App icon:** `assets/icons/icon-512.png` (512×512)
- **Phone screenshots:** `assets/screenshots/narrow-1.png` to `narrow-4.png` (1080×1920)
- **Desktop screenshots:** `assets/screenshots/wide-1.png` and `wide-2.png` (1920×1080)
- **Privacy policy URL:** https://thinukalehan.github.io/ripple-pond/privacy.html
- **Website / support URL:** https://github.com/ThinukaLehan/ripple-pond

---

## Listing text (copy and paste)

**Name:** Ripple Pond

**Subtitle / short description** (77 characters, fits Google Play's 80):
> A calm koi pond to relax in. Tap for ripples, breathe slowly, let worries go.

**Full description:**
> Ripple Pond is a quiet place to rest your mind for a few minutes.
>
> Tap the water and watch ripples spread while soft notes play. Every note comes from a gentle musical scale, so whatever you tap always sounds peaceful. Koi drift over to see what happened, lily pads bob on the ripples, and a little frog hops between them.
>
> There is no score, no timer and no way to lose. Just a pond, at your own pace.
>
> • Tap for ripples and soft notes. Hold for a bigger stone. Drag your finger to trail through the water.
> • Feed the koi and watch them gather.
> • Breathe with the Pond: follow a lotus that opens as you breathe in and closes as you breathe out (1, 3 or 5 minutes).
> • Let go: write down a worry, set it on a paper boat, and watch it drift away. Nothing you write is ever saved.
> • Sleep mode: the pond plays softly by itself while the screen dims, then fades out on a timer (15, 30 or 60 minutes).
> • The pond follows your own clock: morning mist, bright afternoons, warm sunsets, and moonlit nights with fireflies.
> • Gentle rain, a frog chorus at night, birdsong by day, and a dragonfly that visits on sunny afternoons.
> • Four sound styles: chimes, kalimba, singing bowl and water drops.
> • Works offline. No ads, no accounts, no tracking.
>
> Made for anyone who needs a calm moment, at any age.

**Keywords / tags:** relaxing, calm, meditation, breathing, koi, pond, zen, stress relief, mindfulness, ambient, cozy, sleep

**Category:** Games → Casual (or Health & Fitness if you want it seen as a wellness app)

**Age rating:** Everyone. No violence, no ads, no in-app purchases, no user-to-user communication, collects no data.

---

## itch.io

1. Sign in at https://itch.io and choose **Upload new project**.
2. **Title:** Ripple Pond. **Short description:** use the short description above.
3. **Kind of project:** HTML.
4. **Uploads:** upload `release/ripple-pond-itch.zip` (run `python scripts/package_itch.py` after building to make it) and tick **This file will be played in the browser**.
5. **Embed options:** viewport 960 × 600, tick **Mobile friendly** (orientation: default), **Automatically start on page load**, and **Fullscreen button**.
6. **Classification:** Games. **Genre:** Simulation. **Tags:** relaxing, cozy, meditation, ambient, casual, singleplayer, atmospheric, short.
7. **Pricing:** "No payments" or "$0 or donate". Donations are optional.
8. Add the screenshots and set the cover image (630 × 500; crop `wide-1.png`).
9. Save as **Draft**, open the page to try it, then set visibility to **Public**.

---

## Microsoft Store (free for individuals)

1. Create a free individual developer account at https://partner.microsoft.com (Windows & Xbox → individual).
2. In Partner Center: **Apps and games → New product → MSIX or PWA app**, and reserve the name **Ripple Pond**.
3. Open the new app's **Product identity** page. Keep it open: you need its *Package/Identity/Name*, *Publisher*, and *Publisher display name*.
4. Go to https://www.pwabuilder.com, enter `https://thinukalehan.github.io/ripple-pond/` and start.
5. Choose **Package for stores → Windows**, paste the three values from step 3, and download the package.
6. Back in Partner Center, create a **submission**: upload the `.msixbundle` from the download, set pricing to free, add the description, screenshots and age rating, set the privacy policy URL, and submit for certification (usually a few days).

---

## Google Play ($25 one-time)

New personal developer accounts must run a **closed test with at least 12 testers for 14 days in a row** before the app can go public. Line up 12 friends or family with Android phones before you start.

1. Create a developer account at https://play.google.com/console and pay the $25 fee. Identity verification can take a few days.
2. Go to https://www.pwabuilder.com, enter `https://thinukalehan.github.io/ripple-pond/`, and choose **Package for stores → Android**.
   - **Package ID:** `io.github.thinukalehan.ripplepond`
   - **App name:** Ripple Pond. **Display mode:** standalone.
   - Let PWABuilder create a new signing key.
3. Download the package. It contains:
   - the `.aab` file to upload to Play,
   - `signing.keystore` and its passwords. **Keep these safe and private.** Without them you can never update the app. Never commit them to GitHub.
   - `assetlinks.json`, which proves to Android that the app and the website belong together.
4. **Publish `assetlinks.json` (so the app opens without a browser address bar).** Android looks for it at the root of the domain, `https://thinukalehan.github.io/.well-known/assetlinks.json`, not inside `/ripple-pond/`. To host it:
   - Create a new public GitHub repo named exactly `ThinukaLehan.github.io`.
   - Add the file at `.well-known/assetlinks.json`, plus an empty file named `.nojekyll` at the root (otherwise GitHub Pages hides folders starting with a dot).
   - Turn on Pages for that repo (Settings → Pages → deploy from `main`, root).
5. In Play Console, **Create app** (name Ripple Pond, Game, Free), then fill in:
   - **Privacy policy:** https://thinukalehan.github.io/ripple-pond/privacy.html
   - **Data safety:** no data collected, no data shared.
   - **Content rating questionnaire:** answer "no" to everything, which gives Everyone / PEGI 3.
   - **Ads:** no ads. **Target audience:** pick the age groups you want. Including under-13s adds Google's Families policy review, which Ripple Pond meets (no ads, no data), but it takes longer.
   - **Store listing:** text above, the 512 icon, phone screenshots, and a 1024 × 500 feature graphic (crop `wide-1.png`).
6. Upload the `.aab` to **Testing → Closed testing**, add your 12+ testers' Google account emails, and send them the opt-in link. Keep the test running for 14 days.
7. **Play App Signing:** Google re-signs the app, so open **Setup → App integrity**, copy the *App signing key certificate* SHA-256 fingerprint, and add it to the `sha256_cert_fingerprints` list in `assetlinks.json` (keep PWABuilder's one too). Push the change.
8. After 14 days, apply for **production access** in the dashboard, then release to production.

---

## Updating the published game

1. Change the source, run `node scripts/build.mjs`, run the tests, commit and push.
2. The website and every installed copy (home screen, Microsoft Store and Google Play) update automatically, because they all load the game from the website.
3. Only re-upload to a store when the store listing itself changes (name, icon or screenshots). Re-upload the itch.io zip after each update (run `python scripts/package_itch.py`).

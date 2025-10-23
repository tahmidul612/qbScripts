# Project Plan: qBittorrent Peer-IP Clustering & ProtonVPN Server Recommender

## 📌 Task Breakdown and Implementation Checklist

- **Project setup:** Initialize a new Python project using uv. Scaffold the repository (src/ for code, tests/ for tests, docs/ for documentation), a pyproject.toml, and basic docs/README. Use uv init or equivalent to create a Python package and venv[[1]](https://realpython.com/python-uv/#:~:text=The%20main%20idea%20behind%20these,100%20times%20faster%20than%20pip). Adopt **semantic versioning** (SemVer) from the start (we’ll auto-bump versions based on commit types[[2]](https://www.conventionalcommits.org/en/v1.0.0/#:~:text=How%20does%20this%20relate%20to,SemVer)) and enforce a **conventional commit** style (e.g. feat:, fix:) to drive releases[[2]](https://www.conventionalcommits.org/en/v1.0.0/#:~:text=How%20does%20this%20relate%20to,SemVer). Configure uv to install dev tools (e.g. pytest, ruff, black).

- **Dependency management with UV:** Use the uv tool to manage the project environment and dependencies. For example, uv add qbittorrent-api requests rich cachetools folium geopy numpy scikit-learn pytest to install core libraries, and use uv lock to lock a fast, reproducible environment[[1]](https://realpython.com/python-uv/#:~:text=The%20main%20idea%20behind%20these,100%20times%20faster%20than%20pip). uv can create the virtualenv, pin dependencies, and even run scripts, providing an integrated workflow[[1]](https://realpython.com/python-uv/#:~:text=The%20main%20idea%20behind%20these,100%20times%20faster%20than%20pip).

- **Coding standards & linting:** Set up a pre-commit configuration (e.g. via [pre-commit](https://pre-commit.com/)) that runs ruff (fast Rust-based linter/formatter) and black/isort. Ruff is much faster than legacy linters (10–100× faster than Flake8 or Black[[1]](https://realpython.com/python-uv/#:~:text=The%20main%20idea%20behind%20these,100%20times%20faster%20than%20pip)). Use a commit-msg hook (commitlint) to enforce conventional commit messages. Document these conventions in CONTRIBUTING.md.

- **Peer data gathering:** Implement a module qbit_peer_fetcher that connects to qBittorrent’s Web UI via qbittorrent-api. Example: instantiate qbittorrentapi.Client and call client.sync.torrent_peers(torrent_hash=..., rid=0) for each active torrent to retrieve its peer list[[3]](https://qbittorrent-api.readthedocs.io/_/downloads/en/latest/pdf/#:~:text=Usage%20,sync_maindata%28rid%3D0%2C%20%2A%2Akwargs%29%20%E2%86%92%20SyncMainDataDictionary). Aggregate all peer IP addresses and counts. (Write unit tests mocking Client so no actual qBittorrent is needed.)

- **IP Geolocation service:** Build a geolocator module that takes an IP address and returns latitude/longitude and location info. Primary lookup will use **IP-API.com** (free JSON API, no key needed, up to 45 req/min, returns country, city, lat, lon)[[4]](https://ip-api.com/#:~:text=IP,and%20reliable%20IP%20Geolocation%20API). Implement a **TTL cache** (e.g. cachetools.TTLCache) so each unique IP is only looked up once per time window[[5]](https://cachetools.readthedocs.io/en/latest/#:~:text=class%20cachetools). On cache miss or API error (HTTP error or rate-limit), fall back to a secondary provider (e.g. IPinfo or IPapi). IPinfo’s official Python library has built-in caching support and bulk lookup features[[6]](https://ipinfo.io/blog/geolocation-api-python#:~:text=IPinfo%20Python%20Library)[[7]](https://ipinfo.io/blog/geolocation-api-python#:~:text=Going%20beyond%20the%20standard%20IP,many%20more%20features%2C%20such%20as). Write tests to simulate caching logic and provider fallback (e.g. mock requests to return errors).

- **Determine current IP location:** Implement a function (e.g. get_current_location()) that queries a public “what is my IP” endpoint (for instance ip-api.com/json/) to get the user’s public IP and geolocation. Cache it similarly (it won’t change often).

- **ProtonVPN server data:** Fetch the ProtonVPN server list JSON from the Huzky repository (raw URL) or maintain an updated copy. Parse the JSON and filter for P2P-enabled servers ("P2P Feature Enabled": true). Store relevant fields (server name, city, country, IPs). This data can be refreshed on demand or on a schedule. Write a small test with a sample JSON snippet to ensure the parser correctly filters P2P servers.

- **Peer clustering and analysis:** From the list of geolocated peer coordinates (with weights = number of peers at that IP), perform a clustering analysis. Options include: (1) **K-Means with sample weights** (Scikit-learn’s KMeans(..., sample_weight=...)), (2) **Hierarchical/DBSCAN clustering** based on geographic distance (e.g. Haversine) to find dense peer groups. Compute the centroid of each cluster (weighted by peer counts). Also compute the overall weighted centroid of all peers.

- **Server recommendation algorithm:** For each cluster centroid, compute geodesic distances (using e.g. geopy.distance) to all candidate ProtonVPN servers. Rank servers by proximity *and* P2P support. For weighting, larger clusters can influence choice by repeating server suggestions or by scoring (e.g. a score = (cluster_peer_count) / (distance + ε)). Select the top server(s) that minimize weighted distance. Also consider the user’s current location as a factor: e.g. favor VPN servers closer to both user and peer centroids. Document this algorithmic approach.

- **Terminal UI Output:** Create a CLI (using **Typer** or **Click**) that runs the analysis. Use **Rich** to display results: e.g. a table of clusters (peer count, centroid location, suggested VPN server, distance). Use colored highlights or icons. Optionally, explore **Textual** for a more interactive interface (though a full map in terminal is advanced; it might suffice to display key info). Test that the CLI runs without errors and formats output cleanly on terminals (e.g. Kitty, iTerm).

- **Map visualization (optional):** Offer an option --map to output an HTML map. Use **Folium** (built on Leaflet) or **Plotly** to create an interactive map: plot peer locations (clustered markers or heatmap) and lines to chosen VPN server(s). Use reverse geocoding (geopy.Nominatim) to label cities/countries at centroids. Add a legend explaining markers. For light/dark mode, switch Folium tile layers (e.g. CartoDB Positron for light, CartoDB DarkMatter for dark). Folium supports built-in tiles like "CartoDB Positron"[[8]](https://python-visualization.github.io/folium/latest/reference.html#:~:text=%3E%20%20%20,) and custom layers. If not using Folium, use another lightweight mapping library that supports these features. Include HTML tests (e.g. verify file output and presence of key text).

- **Documentation & CI:** Write thorough README.md with usage examples. Include a CONTRIBUTING.md outlining branch and commit conventions (e.g. feat/xyz, bugfix/abc, etc.). Set up CI (GitHub Actions) to run uv install, ruff --check, and pytest on each PR. Ensure the CI fails on style or test errors. Use pytest-cov to track test coverage.

## 🧠 Key Design Decisions

- **Modular Architecture:** The tool will be a reusable Python package (src/qb_peer_vpn/), importable by other scripts. Core modules include: peer_fetcher, geolocator, vpn_data, cluster_analyzer, and ui (CLI and map). This separation aids testing and reuse.

- **Caching & Robust Geolocation:** To respect free API rate limits and speed up repeated runs, we cache IP geolocation results with TTL (e.g. 24h expiration) using cachetools.TTLCache[[5]](https://cachetools.readthedocs.io/en/latest/#:~:text=class%20cachetools). We will design the geolocator interface to transparently try multiple providers: first ip-api.com (free, JSON, no key[[4]](https://ip-api.com/#:~:text=IP,and%20reliable%20IP%20Geolocation%20API)), then fallback to a secondary (e.g. IPinfo or ipapi) on failure or throttling. This provider chain is configurable for reliability.

- **Clustering Algorithm:** We will use a centroid-based clustering approach. For simplicity, start with a weighted K-Means (with sample_weight = peer counts) to group peer coordinates, as it naturally finds centroids that minimize distance squared. If finer control is needed, we may try DBSCAN (with a geographic radius threshold) or hierarchical clustering to find natural clusters. The final server choice may be the one nearest the largest-weighted cluster, or possibly multiple servers for multiple clusters.

- **Distance Metric:** Distances will be calculated as geodesic (great-circle) distances. We should use a reliable library (e.g. geopy.distance.geodesic) to compute distances between latitude/longitude points. This avoids distortions for long distances.

- **ProtonVPN Data Handling:** Rather than re-scrape or login to ProtonVPN endpoints, we rely on the maintained JSON list. This is a straightforward HTTP GET of a raw GitHub URL (or an updated local snapshot). We parse JSON and **filter by "P2P Feature Enabled": true**. Store these server entries in a simple list/dict for distance queries.

- **CLI vs GUI:** A text-based report is primary (for a pure terminal workflow). We use **Rich** for formatting (tables, colored text). Full graphical maps in terminal are complex; if Textual’s graphics support is limited, we default to generating an external HTML/JS map. The HTML map uses Folium so users can open it in a browser if desired, with interactive zoom. Folium supports custom tile layers for theme, and adding a legend or control layers.

- **Visualization Details:** On the map, we’ll plot: peer locations (clustered markers or grouped heat points), cluster centroids labeled by city/country, lines connecting centroid to suggested VPN server(s), and markers for VPN servers. Include a legend (e.g. color-coded points for peers vs servers). For light/dark mode, use a tile like CartoDB Positron (light) vs CartoDB DarkMatter (dark)[[8]](https://python-visualization.github.io/folium/latest/reference.html#:~:text=%3E%20%20%20,). Folium (via folium.Map(tiles="CartoDB Positron")) makes this easy[[8]](https://python-visualization.github.io/folium/latest/reference.html#:~:text=%3E%20%20%20,).

- **Versioning & Commits:** Enforce **Semantic Versioning**. Adopt Conventional Commits (e.g. feat: add clustering, fix: handle no peers) so that we can auto-generate changelogs and bump versions systematically[[2]](https://www.conventionalcommits.org/en/v1.0.0/#:~:text=How%20does%20this%20relate%20to,SemVer). For example, all fix: commits result in a patch increment, feat: commits a minor, and any BREAKING CHANGE signals a major version bump[[2]](https://www.conventionalcommits.org/en/v1.0.0/#:~:text=How%20does%20this%20relate%20to,SemVer).

- **Terminal Environment:** Assume a modern terminal (e.g. Kitty) with UTF-8 and color support. Rich will auto-detect color capabilities. We should ensure any Unicode/ASCII used in tables is widely supported.

## 🛠️ Recommended Libraries and Fallbacks

- **qBittorrent API:** Use the qbittorrent-api Python package (official client) to interface with qBittorrent’s Web API. It provides methods like client.sync.torrent_peers(...)[[3]](https://qbittorrent-api.readthedocs.io/_/downloads/en/latest/pdf/#:~:text=Usage%20,sync_maindata%28rid%3D0%2C%20%2A%2Akwargs%29%20%E2%86%92%20SyncMainDataDictionary) to retrieve peer info.

- **HTTP Requests:** Use httpx or requests for simplicity (both work well with the geolocation APIs and downloading JSON).

- **Caching:** Use cachetools.TTLCache for in-memory caching of IP lookups[[5]](https://cachetools.readthedocs.io/en/latest/#:~:text=class%20cachetools). Optionally, requests_cache could persist to disk (not required but possible).

- **Geolocation APIs:**

- *Primary:* **IP-API.com** (free JSON API, no API key, fast)[[4]](https://ip-api.com/#:~:text=IP,and%20reliable%20IP%20Geolocation%20API). E.g. GET http://ip-api.com/json/\<IP>?fields=status,country,city,lat,lon.

- *Fallback:* **IPinfo.io** (free tier with token). Its official Python library supports caching and batch queries[[6]](https://ipinfo.io/blog/geolocation-api-python#:~:text=IPinfo%20Python%20Library)[[7]](https://ipinfo.io/blog/geolocation-api-python#:~:text=Going%20beyond%20the%20standard%20IP,many%20more%20features%2C%20such%20as). Or **ipapi.co** (also free with limits) as an alternate.

- *Local IP:* For obtaining current IP, use ip-api.com/json/ with no IP parameter (it returns caller’s IP info).

- **Clustering/Math:** Use **NumPy** for data structures and **scikit-learn**’s clustering (e.g. KMeans with sample_weight for weighted centroid). SciPy’s spatial.distance or scikit-learn’s pairwise_distances for calculating distance matrices. For geodesic distance, use **geopy** or implement the Haversine formula via numpy.

- **Geocoding:** Use **geopy**’s Nominatim for reverse geocoding of coordinates to nearest city/country (for map labels). It’s free but rate-limited; cache these results too.

- **CLI:** Use **Typer** (built on Click) for a clean CLI interface with type annotations, or **argparse** if you prefer stdlib. Typer makes help strings and options easy.

- **Terminal Output:** Use **Rich** to print tables, panels, and progress bars. Rich can also render (static) images or emojis if needed. For more interactive UIs, consider **Textual** (which extends Rich), but for a first version Rich alone suffices for formatted output.

- **Mapping (HTML):** Use **Folium** for an interactive Leaflet map. Folium supports adding tile layers (e.g. CartoDB Positron for light mode)[[8]](https://python-visualization.github.io/folium/latest/reference.html#:~:text=%3E%20%20%20,). It also supports adding lines (folium.PolyLine) and markers with pop-ups. If Folium is too heavy, **Plotly**’s map features are an alternative, but Folium is more straightforward for leaflet styling.

- **Styling:** For code style, rely on **Black** (autoformatter) and **isort** (import sorting) via pre-commit. **Ruff** will catch both lint issues and auto-format (it can replace Black if desired, but Black is standard).

- **Testing:** Use **pytest** for unit/integration tests. Plugins: pytest-cov for coverage. Optionally pytest-mock or unittest.mock for mocking external calls.

- **Other Tools:**

- **pre-commit** to glue linters, formatters, and commit-msg hooks.

- **commitizen** or **commitlint** for enforcing conventional commit messages.

- **GitHub Actions** or similar CI to run tests, lint, and security scans on each PR.

## 🧪 Testing and Validation Strategy

- **Unit tests (pytest):** For each module/component:

- *Peer Fetcher:* Mock a qbittorrentapi.Client object to simulate returned torrent and peer data. Verify the parsing logic extracts IPs correctly.

- *Geolocator:* Use HTTP mocking (e.g. responses or pytest-httpx) to simulate IP-API responses. Test that caching works (calling the same IP twice hits cache second time). Also mock a failure of primary API to ensure the fallback provider is invoked.

- *VPN Data:* Test JSON parsing logic with a sample snippet of the ProtonVPN list. Ensure only P2P entries remain.

- *Clustering:* Create synthetic coordinates with known clusters. Verify that the clustering code correctly identifies centroids (e.g. cluster two sets of points and ensure outputs match).

- *Server Matching:* Given known coordinates and a small server list, test that the nearest server is chosen.

- *CLI:* Use Typer’s CliRunner to invoke the command with sample data and capture output. Assert that expected strings (e.g. city names, server names) appear.

- *Map Generation:* Test that the HTML file is created and contains expected markers (search for a known location or server name in the HTML).

- **Integration tests:** Simulate end-to-end runs by overriding APIs to return fixed data (monkeypatch geolocator to return preset coordinates for IPs, override qbittorrent client). Assert the final recommendations match expectations.

- **Test Coverage:** Aim for high coverage on all branches. Use CI to enforce a minimum threshold (e.g. 90% coverage).

- **Continuous Validation:** In code, add assertions or sanity checks (e.g. if no peers found, print a message). Log intermediate results (using rich.logging or prints) for debugging.

- **Data Validation:** After implementing each step, print sample outputs to verify correctness. For example, after geolocation, print IP and coords to ensure lookups are reasonable. After clustering, print cluster centroids vs peer data to verify grouping.

- **Fallback Logic:** Specifically test that when ip-api.com returns an error or slow response, the code properly tries the next service. For instance, simulate an HTTP 500 or 429 from IP-API and ensure IPinfo is then used.

## 🔁 Workflow Automation (Pre-commit, UV, CI)

- **Pre-commit hooks:** Create a .pre-commit-config.yaml that runs:

- ruff --fix (or ruff --check) on Python files,

- black --check, isort --check for formatting,

- commitlint (or a small script) on commit messages to enforce the type(scope): description format.
  This ensures code style and commit style automatically.

- **uv project scripts:** In pyproject.toml (or via uv), define common commands:

- uv run lint → runs ruff/black.

- uv run test → runs pytest.

- uv run format → runs black --apply and isort.

- uv run bump → uses commit history to bump version (if using a release tool).
  This allows easy local invocation (e.g. uv run lint) and consistent CI steps.

- **CI Pipeline:** On each push/PR:

- Install dependencies via uv sync or pip install .[dev].

- Run ruff --check . to ensure no lint errors.

- Run uv run test (i.e. pytest --maxfail=1 --disable-warnings) to execute tests.

- Optionally, build docs or check markdown links (if using MkDocs or similar).

- Use a coverage action to fail if below threshold.

- **Semantic Releases:** Optionally use a GitHub Action (e.g. [semantic-release](https://github.com/semantic-release/semantic-release)) that reads conventional commits to auto-update version and changelog on merges to main. This ties into our semantic versioning approach[[2]](https://www.conventionalcommits.org/en/v1.0.0/#:~:text=How%20does%20this%20relate%20to,SemVer).

- **Branching Policy:** Use feature branches (naming like feature/geo-cache, feature/cluster-algo) for all work. Only merge into main via Pull Requests. Protect main branch. Name commits using conventional prefixes (e.g. feat: add weighted clustering) as documented in CONTRIBUTING.md.

- **Dependency Updates:** Manage dependencies with uv; lock file ensures repeatable builds. For routine updates, use uv up or uv upgrade. Add Dependabot (or similar) on GitHub to propose updates, then verify via CI.

- **Additional Automation:** Consider a pre-commit hook for pytest (to run a quick smoke test on staged changes). Also, if the project grows, add type-checking (mypy) and security linting (bandit) into CI.

By following this detailed breakdown, leveraging the cited tools and best practices, the library and CLI can be developed in manageable steps, with robust validation and automation ensuring high quality and maintainability[[3]](https://qbittorrent-api.readthedocs.io/_/downloads/en/latest/pdf/#:~:text=Usage%20,sync_maindata%28rid%3D0%2C%20%2A%2Akwargs%29%20%E2%86%92%20SyncMainDataDictionary)[[4]](https://ip-api.com/#:~:text=IP,and%20reliable%20IP%20Geolocation%20API)[[1]](https://realpython.com/python-uv/#:~:text=The%20main%20idea%20behind%20these,100%20times%20faster%20than%20pip)[[2]](https://www.conventionalcommits.org/en/v1.0.0/#:~:text=How%20does%20this%20relate%20to,SemVer).

______________________________________________________________________

[[1]](https://realpython.com/python-uv/#:~:text=The%20main%20idea%20behind%20these,100%20times%20faster%20than%20pip) Managing Python Projects With uv: An All-in-One Solution – Real Python

[https://realpython.com/python-uv/](https://realpython.com/python-uv/)

[[2]](https://www.conventionalcommits.org/en/v1.0.0/#:~:text=How%20does%20this%20relate%20to,SemVer) Conventional Commits

[https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/)

[[3]](https://qbittorrent-api.readthedocs.io/_/downloads/en/latest/pdf/#:~:text=Usage%20,sync_maindata%28rid%3D0%2C%20%2A%2Akwargs%29%20%E2%86%92%20SyncMainDataDictionary) qbittorrent-api

[https://qbittorrent-api.readthedocs.io/\_/downloads/en/latest/pdf/](https://qbittorrent-api.readthedocs.io/_/downloads/en/latest/pdf/)

[[4]](https://ip-api.com/#:~:text=IP,and%20reliable%20IP%20Geolocation%20API) IP-API.com - Geolocation API

[https://ip-api.com/](https://ip-api.com/)

[[5]](https://cachetools.readthedocs.io/en/latest/#:~:text=class%20cachetools) cachetools — Extensible memoizing collections and decorators — cachetools 6.2.1 documentation

[https://cachetools.readthedocs.io/en/latest/](https://cachetools.readthedocs.io/en/latest/)

[[6]](https://ipinfo.io/blog/geolocation-api-python#:~:text=IPinfo%20Python%20Library) [[7]](https://ipinfo.io/blog/geolocation-api-python#:~:text=Going%20beyond%20the%20standard%20IP,many%20more%20features%2C%20such%20as) How to Get Geolocation in Python? - IPinfo.io

[https://ipinfo.io/blog/geolocation-api-python](https://ipinfo.io/blog/geolocation-api-python)

[[8]](https://python-visualization.github.io/folium/latest/reference.html#:~:text=%3E%20%20%20,) API reference — Folium 0.20.0 documentation

[https://python-visualization.github.io/folium/latest/reference.html](https://python-visualization.github.io/folium/latest/reference.html)

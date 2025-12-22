# Understanding By Tier (7 days) in the Empathy Dashboard

The Empathy VS Code dashboard includes a **Cost Details** panel that shows how model routing is saving you money over the last 7 days.

When you click **View Costs** in the Power tab, you’ll see:

- **Saved** – Total dollars saved over the last 7 days compared to always using the premium model.
- **Reduction** – Percentage reduction in cost compared to the premium-only baseline.
- **Actual** – Actual dollars spent on API calls in the last 7 days.

Below the summary, the **By tier (7 days)** section breaks those savings down by model tier:

- **Cheap** – Requests routed to the cheapest tier (e.g., Haiku-level models). Best for simple tasks like short summaries.
- **Capable** – Requests routed to the middle tier (e.g., Sonnet-level models). Used for most code and reasoning tasks.
- **Premium** – Requests routed to the most powerful tier (e.g., Opus-level models). Reserved for the hardest or most critical tasks.

For each tier, you’ll see:

- **Requests** – How many API calls used this tier in the last 7 days.
- **Cost** – Actual dollars spent on that tier.
- **+Saved** – How many dollars you saved by using this tier instead of always using the premium model for those same requests.

Use this section to answer questions like:

- Are most of my requests using **cheap** or **capable** models instead of premium?
- Which tier is responsible for the **largest share of savings**?
- Do I have many **premium** calls that could safely be moved down to capable or cheap?

If the **cheap** and **capable** tiers show healthy savings and most requests, your routing is working well. If **premium** dominates both cost and request count, consider revisiting your task-type to tier mapping in `ModelRouter` or your workflow configuration.

"""Page-specific content for the main marketing pages.

The archived site repeated the same six tiles and the same closing line on almost every page. This
module gives each page its own substance: tiles that describe what that product or trade actually
gets, numbered process steps, proof points, comparison tables and page-specific FAQs. site.py renders
these blocks with the shared design system.

Block types
    features   {"title", "items": [(title, text, icon?)], "cols"?}          tiles with an icon
    steps      {"title", "items": [(title, text)]}                            numbered process
    stats      {"items": [(value, label)]}                                    proof row
    split      {"title", "checks": [...], "photo", "reverse"?, "cta"?}        photo + checklist
    compare    {"title", "cols": (a, b), "rows": [(label, a, b)]}             two-column comparison
    chips      {"title", "items": [...]}                                      list of pages/services we build
    faq        {"title", "items": [(q, a)]}                                   accordion
    quote      {"text", "who", "role", "photo", "href"?}                      large testimonial with photo
    related    {"title", "items": [(title, text, href)]}                      linked cards
    portfolio  {"title", "cat", "href"?}                                      three tiles from the Our Work gallery
    source     {"match": regex}                                               a section from the archived page
    form       {"photo"?, "title"?}                                           free-quote form with a photo backdrop
    app        {}                                                             the mobile-app promo
"""

# ---------------------------------------------------------------------------
# Shared proof
# ---------------------------------------------------------------------------
QUOTE_POHLMAN = {"text": "Since signing on with Charlie Company, our organic website traffic has increased exponentially and we have seen a steady increase in our lead flow. They have solved several of our business challenges with their integration.",
                 "who": "Pohlman Plumbing & HVAC", "role": "Plumbing and HVAC contractor", "photo": "actech"}
QUOTE_DAVID = {"text": "Everyone I have talked with in operating their business app has been so helpful and quick to answer the phone. Their program is so complete for my company to do estimates, invoices, get reviews, make appointments and more.",
               "who": "David K.", "role": "Business owner", "photo": "tablet"}
QUOTE_ERIC = {"text": "Just started using this platform but so far it has been very user friendly, has lots of cool features I didn't expect, and is the best CRM tool I have seen.",
              "who": "Eric R.", "role": "Business owner", "photo": "colleagues"}
QUOTE_PEYTON = {"text": "Customers can make an appointment directly from the website, 24 hours a day. Peyton can send accurate estimates quickly, and the business has received over $1.4 million in customer payments through the platform.",
                "who": "Top Roofing and Contracting", "role": "Kernersville, NC · Case study", "photo": "roofing", "href": "/case-studies/top-roofing-and-contracting/"}
QUOTE_BROTHERS = {"text": "With a website optimized for restaurant and catering keywords, customers find Brothers on the first page of Google. Ronnie has processed over $50,000 in customer payments through the platform.",
                  "who": "Brothers Restaurant & Bar", "role": "Buffalo, NY · Case study", "photo": "chef", "href": "/case-studies/brothers-restaurant-and-bar/"}
QUOTE_AMBER = {"text": "Since implementation, we have zero no-shows. It's worth its weight in gold not just because of our increased earnings and availability, but also because their customer service is superb.",
               "who": "Amber Calleran, Holistic Hounds", "role": "Canine care clinic · Case study", "photo": "vet", "href": "/case-studies/holistic-hounds/"}
QUOTE_ASHLEY = {"text": "Since using Charlie Company Media, my business has expanded by 50%. With one central platform for all my business needs, I have more transparency and order in my business processes.",
                "who": "Ashley Perkins, Perkins Tax & Accounting", "role": "Accounting firm · Case study", "photo": "finance", "href": "/case-studies/perkins-tax-accounting/"}
QUOTE_SHARON = {"text": "I found solutions to keep me away from the computer. I used to spend a full day each week on administration. Now it is only a few hours.",
                "who": "Sharon Boon, Amber Moon Studios", "role": "Fitness and wellness studio · Case study", "photo": "yoga", "href": "/case-studies/amber-moon-studios/"}

PARTNER_STATS = [("23,000+", "Businesses growing with Charlie Company"), ("5,000+", "Five-star Google reviews"), ("76", "Local markets nationwide"), ("No contracts", "We earn your business month to month")]

FORM = {"type": "form"}
APP = {"type": "app"}


def faq_common(product: str) -> list[tuple[str, str]]:
    return [
        ("Is there a long-term contract?", f"No. {product} is month to month. We work to earn your business every month rather than locking you in."),
        ("Who do I talk to when I have a question?", "A US-based support team and a dedicated relationship manager who knows your account. Call (210) 480-6345, Monday to Friday, 9am to 5pm Central, or message us from inside your platform."),
        ("How do I see what it is doing for me?", "Every month you receive a report covering site visits, leads captured, estimates and invoices sent, money collected, messages and appointments. You can also sign in to your platform at any time."),
    ]


# ---------------------------------------------------------------------------
# Grow
# ---------------------------------------------------------------------------
GROW = {
    "/website-design/": {
        "hero_photo": "website",
        "cta": ("Ready for a website that earns its keep?", ("Start a free quote", "#quote-form"), ("See our work", "/our-work/")),
        "blocks": [
            {"type": "stats", "items": [("Mobile-first", "Designed for the phone in your customer's hand"), ("Custom", "Built for your trade, not a template"), ("Unlimited", "Changes and updates, on request"), ("In-house", "Design, content and SEO under one roof")]},
            {"type": "features", "title": "What every website we build includes", "items": [
                ("Service pages that sell", "A dedicated page for each service you offer, written to explain what you do and why customers should call you."),
                ("Service-area pages", "Location pages for every town you cover, so nearby customers find you and understand you work where they live."),
                ("FAQ pages", "Answers to the questions your customers actually ask, which builds trust and captures long, specific searches."),
                ("Click-to-call and quote forms", "Every page makes it easy to call, request an estimate or book, with the lead landing in your inbox and CRM."),
                ("Fast, mobile-responsive build", "Clean navigation, fast-loading pages and a layout that works on every screen size."),
                ("Search-ready structure", "User-friendly URLs, page speed and site structure handled so the site is ready for Search Everywhere Optimization."),
            ]},
            {"type": "source", "match": r"Essential Pages We Create"},
            {"type": "steps", "title": "How your site comes together", "items": [
                ("Onboarding call", "We learn your services, service area, competitors and the jobs you want more of."),
                ("Design and content", "Our in-house team designs the site and writes the service, area and FAQ pages."),
                ("Quality review", "Every page is checked for accuracy, speed and mobile layout before you see it."),
                ("Launch and index", "The site goes live, is submitted to Google, and your monthly reporting begins."),
            ]},
            {"type": "portfolio", "title": "Recent builds", "cat": "Home Services"},
            {"type": "split", "title": "Connected to the tools that run your business", "photo": "tablet", "checks": [
                "Quote requests land in your integrated inbox and CRM", "Online booking writes straight to your calendar", "Estimates, invoices and payments from the same platform", "Automated review requests after every job", "Email and SMS follow-up for every lead"], "cta": ("Explore the platform", "/run/")},
            {"type": "quote", **QUOTE_PEYTON},
            {"type": "faq", "title": "Website design questions", "items": [
                ("Do I have to write the content or supply photos?", "No. Our team writes your service, area and FAQ pages and supplies professional imagery. If you have photos of your crew and work, we will use them."),
                ("How long does a build take?", "Most sites move from onboarding call to launch in a few weeks. Your campaign creation team keeps you updated at every step."),
                ("Can I request changes after launch?", "Yes. Unlimited changes are part of every plan. Send a request to your team and it gets done."),
                ("Do I own my domain?", "Yes. We register and manage the domain in your business name and connect it to your site."),
            ] + faq_common("Website design and management")},
            FORM,
        ],
    },
    "/search-engine-optimization/": {
        "hero_photo": "search",
        "cta": ("Show up wherever your customers search", ("Start a free quote", "#quote-form"), ("Free directory scan", "/directory-scan/")),
        "blocks": [
            {"type": "stats", "items": [("Google", "Organic results and map pack"), ("Directories", "Consistent listings everywhere"), ("AI search", "Content built to be cited by AI answers"), ("Monthly", "Ranking, traffic and lead reporting")]},
            {"type": "source", "match": r"How Our Search Everywhere"},
            {"type": "chips", "title": "Content we build for your campaign", "items": ["Service pages", "Service-area pages", "FAQ pages", "About page", "Evergreen blog articles", "Google Business Profile", "Directory listings", "Review responses"]},
            {"type": "compare", "title": "Search Everywhere Optimization versus old-school SEO", "cols": ("Search Everywhere", "Keywords-only SEO"), "rows": [
                ("Where you show up", "Google results, map pack, directories and AI answers", "Blue links only"),
                ("Content", "Service, area, FAQ and blog pages written for intent", "A few keywords on the home page"),
                ("Local signals", "Name, address and phone consistent across major directories", "Left to chance"),
                ("Technical work", "Speed, mobile usability and site structure handled", "Rarely touched"),
                ("Reporting", "Monthly rankings, traffic and lead flow", "A rank-tracker screenshot"),
            ]},
            {"type": "quote", **QUOTE_POHLMAN},
            {"type": "source", "match": r"Why Our Search Everywhere"},
            {"type": "faq", "title": "Search questions", "items": [
                ("How soon will I see results?", "New pages are usually indexed within weeks. Rankings and lead flow build over the first few months and keep compounding as content, listings and reviews grow."),
                ("Can you guarantee the top spot on Google?", "No one can honestly promise a position. We build the consistent presence search engines and AI systems reward and report the results every month."),
                ("What is AI-aware content?", "Clear, well-structured pages that AI summaries and conversational answers can accurately reference, without unproven tactics."),
                ("Do you handle my Google Business Profile?", "Yes. Profile management, categories, photos, posts and review responses are part of the campaign."),
            ] + faq_common("Search Everywhere Optimization")},
            FORM,
        ],
    },
    "/business-listings/": {
        "hero_photo": "local",
        "cta": ("Be accurate everywhere customers look", ("Run a free directory scan", "/directory-scan/"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "stats", "items": [("Up to 35", "Authoritative directories kept accurate"), ("One source", "Your details managed from one place"), ("Duplicates", "Suppressed so only real listings show"), ("Monthly", "Listing performance in your report")]},
            {"type": "features", "title": "What listing management covers", "items": [
                ("Name, address and phone everywhere", "Your business details published consistently across Google, Apple, Bing, Yelp, Facebook and the directories customers use."),
                ("Hours, services and categories", "Holiday hours, service lists and categories kept current so nobody drives to a closed door."),
                ("Duplicate suppression", "Old or duplicate listings are found and suppressed so only authentic listings are displayed."),
                ("Google Business Profile", "Photos, posts, products and review responses managed as part of your campaign."),
                ("Listing performance", "Views, clicks, calls and direction requests reported so you see what your listings produce."),
                ("Stronger local rankings", "Consistent citations are one of the signals behind the map pack and AI answers."),
            ]},
            {"type": "steps", "title": "How we get your listings right", "items": [
                ("Scan", "We audit where your business appears today and where the details are wrong or missing."),
                ("Clean up", "Wrong numbers, old addresses and duplicates are corrected or suppressed."),
                ("Publish", "Accurate details, hours, services and photos go out to every major directory."),
                ("Monitor", "Listings are watched for unauthorized changes and reported monthly."),
            ]},
            {"type": "split", "title": "Check your listings in seconds", "photo": "search", "reverse": True, "checks": ["See which directories list you and which do not", "Spot wrong phone numbers, addresses and hours", "Find duplicate listings competing with you", "Get a clear report, free, with no obligation"], "cta": ("Run my free scan", "/directory-scan/")},
            {"type": "faq", "title": "Listing questions", "items": [
                ("Which directories do you manage?", "The major search, map and review platforms plus industry and local directories, up to 35 authoritative sites."),
                ("I moved. How fast do listings update?", "Most directories update within days of the change going out from our platform. We monitor until every listing reflects the new address."),
                ("Does this help my Google ranking?", "Yes. Consistent citations are a core local ranking signal, and accurate listings drive calls and directions directly."),
            ] + faq_common("Listing management")},
            FORM,
        ],
    },
    "/reputation-management/": {
        "hero_photo": "reviews",
        "cta": ("Turn happy customers into five-star reviews", ("Start a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "stats", "items": [("Every review", "Alerts the moment a new one is posted"), ("Automated", "Review requests after every job"), ("Help", "Crafting responses to tough reviews"), ("5,000+", "Five-star reviews earned by our clients")]},
            {"type": "features", "title": "How reputation management works", "items": [
                ("New-review notifications", "A notification for every new review and rating your business receives, wherever it is posted."),
                ("Automated review requests", "After every completed job or invoice the platform asks the customer for a review by email or text."),
                ("Response help", "Positive or negative, a quick and tactful reply matters. We help you craft a solid response."),
                ("Google, Facebook and more", "Reviews monitored across the platforms where customers make their decision."),
                ("Reviews on your website", "Fresh reviews displayed on your site to build trust with visitors who are ready to call."),
                ("Ranking impact", "Review volume, recency and responses feed Google's local results and AI answers."),
            ]},
            {"type": "steps", "title": "From finished job to five stars", "items": [
                ("Job completed", "You mark the job done or send the invoice from the platform."),
                ("Request sent", "The customer receives a short, branded request with a direct link to review you."),
                ("Review posted", "You are notified immediately and can respond from your inbox."),
                ("Reputation grows", "New reviews appear on your site and lift your local visibility."),
            ]},
            {"type": "quote", **QUOTE_DAVID},
            {"type": "faq", "title": "Review questions", "items": [
                ("Can you remove a bad review?", "No one can remove legitimate reviews. We help you respond well, flag reviews that break platform rules, and bury the odd bad one with a steady stream of new five-star reviews."),
                ("Which platforms are monitored?", "Google, Facebook and the major review and directory sites relevant to your industry."),
                ("Does the customer have to download anything?", "No. The request is a simple text or email with a link that opens the review form."),
            ] + faq_common("Reputation management")},
            FORM,
        ],
    },
    "/social-media-marketing/": {
        "hero_photo": "social",
        "cta": ("Keep your business in your customers' feeds", ("Start a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "stats", "items": [("2x weekly", "Posts written and published for you"), ("Facebook", "Page set up, branded and maintained"), ("Managed", "Our team engages with your followers"), ("Local", "Content built around your area and services")]},
            {"type": "features", "title": "What managed social media includes", "items": [
                ("Page setup and branding", "Your business Facebook page built, branded and made easy to share and link to."),
                ("Two posts a week", "Customer-centric content posted twice a week so your page never looks abandoned."),
                ("Engagement", "Our social team responds to comments and engages with followers and ideal customers."),
                ("Reviews and jobs featured", "Finished work, five-star reviews and seasonal offers turned into posts."),
                ("Audience research", "We identify who your best customers are and put your content in front of people like them."),
                ("Findability", "An active page strengthens how easily people can find you online."),
            ]},
            {"type": "chips", "title": "Post ideas we turn into content", "items": ["Before and after photos", "Five-star reviews", "Seasonal reminders", "Meet the crew", "Service spotlights", "Promotions and offers", "Community events", "Tips and how-tos"]},
            {"type": "related", "title": "Pair it with", "items": [
                ("Targeted Social Ads", "Put paid ads in the Facebook and Instagram feeds of your ideal customers.", "/targeted-social-ads/"),
                ("Reputation Management", "Keep the five-star reviews coming so there is always something to post.", "/reputation-management/"),
                ("Automated Email & SMS", "Follow up with the leads your social presence creates.", "/automated-email-and-sms/"),
            ]},
            {"type": "faq", "title": "Social media questions", "items": [
                ("Do I need to send you content?", "No. Photos of your work and team are welcome, but our team writes and schedules the posts either way."),
                ("Which platforms?", "Managed posting focuses on your Facebook business page. Paid campaigns on Facebook and Instagram are available through Targeted Social Ads."),
                ("Can I approve posts?", "Yes. Tell your team how hands-on you want to be and we will work that way."),
            ] + faq_common("Social media marketing")},
            FORM,
        ],
    },
    "/targeted-social-ads/": {
        "cta": ("Reach the people most likely to hire you", ("Start a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "stats", "items": [("Facebook", "and Instagram placements"), ("Targeted", "By location, age, interests and behavior"), ("Managed", "Creative, targeting and budget handled"), ("Reported", "Reach, clicks and leads every month")]},
            {"type": "features", "title": "How targeted social advertising works", "items": [
                ("Audience targeting", "Ads aimed at the exact demographics, interests and behaviors of the people who need your service."),
                ("Geographic focus", "Campaigns run only in the towns and neighborhoods you serve, so no budget is wasted."),
                ("Ad creative", "Images, copy and offers built by our team to match your brand and your season."),
                ("Lead capture", "Ads point to your site, a booking page or a lead form that lands in your platform."),
                ("Retargeting", "People who visited your website see you again in their feed while they decide."),
                ("Optimization", "Budgets and audiences adjusted as results come in, with everything in your monthly report."),
            ]},
            {"type": "steps", "title": "Launching your campaign", "items": [
                ("Goal and offer", "New customers, seasonal promotion, hiring or brand awareness. We start with the outcome."),
                ("Audience build", "Your service area, ideal customer and past visitors define who sees the ads."),
                ("Creative and launch", "Ads are designed, approved with you and launched on Facebook and Instagram."),
                ("Refine and report", "Performance is monitored and budgets move to the audiences that convert."),
            ]},
            {"type": "related", "title": "Works best with", "items": [
                ("Targeted Display Ads", "Follow your audience across 16 million websites and apps.", "/targeted-display-ads/"),
                ("Lead Conversion Tool", "Make sure every click can book, call or pay in a few taps.", "/lead-conversion-tool/"),
                ("Social Media Marketing", "An active page makes your ads more credible.", "/social-media-marketing/"),
            ]},
            {"type": "faq", "title": "Social advertising questions", "items": [
                ("How much should I spend?", "Budgets are set around your market and goals. Your team will recommend a starting point and adjust as results come in."),
                ("Where do the leads go?", "Calls, form fills and bookings from your ads land in your integrated inbox and CRM, and you are notified by text."),
                ("Can I pause for the slow season?", "Yes. Campaigns can be paused, shifted or re-targeted at any time."),
            ] + faq_common("Targeted social advertising")},
        ],
    },
    "/targeted-display-ads/": {
        "cta": ("Put your business where your customers already are", ("Start a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "stats", "items": [("16M+", "Websites and apps in the programmatic network"), ("Local", "Ads shown only in the areas you serve"), ("Pay per click", "Search ads cost only when someone clicks"), ("Reported", "Impressions, clicks and calls monthly")]},
            {"type": "features", "title": "Three ways to get in front of your audience", "items": [
                ("Search engine marketing", "Be the first thing people see when they search on Google, paying only when someone clicks."),
                ("Programmatic display", "Your ads placed across 16 million websites and apps where your ideal customers spend time."),
                ("Customer targeting", "Audiences built from what people are researching online, so your ad reaches them while they decide."),
                ("Retargeting", "Visitors who left your website keep seeing you across the web until they come back."),
                ("Local placement", "Popular local websites and apps in your market, with precision by zip code."),
                ("Conversion tracking", "Calls, forms and bookings tied back to the campaign in your monthly report."),
            ]},
            {"type": "compare", "title": "Display advertising versus a billboard", "cols": ("Targeted display", "Traditional billboard"), "rows": [
                ("Who sees it", "People in your area researching your service", "Everyone driving past"),
                ("Measurement", "Impressions, clicks, calls and forms", "None"),
                ("Changes", "Creative and targeting updated any time", "Locked for the contract"),
                ("Follow-up", "Retargets visitors who did not act", "One shot"),
            ]},
            {"type": "faq", "title": "Display advertising questions", "items": [
                ("What is programmatic advertising?", "Automated buying of ad space across a network of websites and apps, targeted by location and interest instead of a single publisher."),
                ("Will my ads show on sites I would not want?", "Placements are filtered for brand safety and focused on reputable local and national sites and apps."),
                ("How is this different from social ads?", "Social ads live in Facebook and Instagram feeds. Display and search ads reach people across Google and the wider web."),
            ] + faq_common("Targeted display advertising")},
        ],
    },
    "/lead-conversion-tool/": {
        "cta": ("Stop losing the leads your marketing already earns", ("Start a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "stats", "items": [("Book", "Appointments in a few clicks"), ("Call", "Click-to-call from every page"), ("Pay", "Deposits and invoices online"), ("Text alerts", "The moment a lead comes in")]},
            {"type": "features", "title": "What the lead conversion tool does", "items": [
                ("Instant booking", "Visitors pick a time from your live availability and the appointment lands on your calendar."),
                ("Click-to-call", "A prominent call button on every page, tracked so you know which pages drive calls."),
                ("Get paid online", "Customers can pay a deposit or an invoice right from your website."),
                ("Text notifications", "Whenever the tool captures a lead you are notified by text message, so nothing slips."),
                ("Lead records", "Every booking, call and payment creates a contact in your CRM with the full history."),
                ("Automatic follow-up", "New leads get a confirmation and a follow-up sequence by email or SMS."),
            ]},
            {"type": "steps", "title": "From visitor to booked job", "items": [
                ("Visitor lands", "From Google, a listing, an ad or a social post."),
                ("Takes action", "Books a time, taps to call or requests an estimate."),
                ("You are alerted", "A text hits your phone and the lead appears in your inbox."),
                ("Job is booked", "Confirmation goes out automatically and the job sits on your calendar."),
            ]},
            {"type": "quote", **QUOTE_AMBER},
            {"type": "faq", "title": "Lead conversion questions", "items": [
                ("Does it work with my existing website?", "It is built into the websites we design and manage, so booking, calls and payments are wired in from launch."),
                ("What if I miss the text?", "The lead is also in your integrated inbox and CRM, and automated follow-up keeps the customer warm until you respond."),
                ("Can customers choose which service they book?", "Yes. Services, durations and availability are configured in your integrated calendar."),
            ] + faq_common("The lead conversion tool")},
        ],
    },
    "/monthly-reporting/": {
        "cta": ("Know exactly what your marketing is doing", ("Start a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "stats", "items": [("Every month", "A report in your inbox and your platform"), ("6 metrics", "That tie marketing to money"), ("Plain English", "No jargon, no vanity numbers"), ("Your team", "Walks you through it on request")]},
            {"type": "features", "title": "What your monthly report tracks", "items": [
                ("Monthly site visits", "Visitor volume and trends so you can see peak engagement periods and seasonality."),
                ("Leads captured", "Forms, bookings and inquiries collected, so you know what your visibility produced."),
                ("Estimates and invoices sent", "The quotes and invoices issued through the platform, a clear view of transactional activity."),
                ("Money collected", "Revenue collected from clients through the platform for cash-flow tracking."),
                ("Messages sent and received", "Total conversations with customers and prospects, a measure of responsiveness."),
                ("Appointments scheduled", "Bookings set through your site and calendar, to plan capacity and staffing."),
            ]},
            {"type": "split", "title": "Search rankings and listings, too", "photo": "reporting", "checks": ["Keyword rankings for the searches that bring jobs", "Google Business Profile views, calls and direction requests", "Directory listing accuracy and performance", "Review count and rating over time"], "cta": ("Explore Search Everywhere Optimization", "/search-engine-optimization/")},
            {"type": "faq", "title": "Reporting questions", "items": [
                ("Where do I see the report?", "It is emailed to you each month and available any time when you sign in to your platform."),
                ("Can someone explain the numbers?", "Yes. Your relationship manager will review the report with you and recommend next steps."),
                ("Is my data shared?", "No. Your reporting and customer data belong to your business."),
            ] + faq_common("Monthly reporting")},
        ],
    },
    "/online-ordering/": {
        "hero_photo": "chef",
        "eyebrow": "Grow · Restaurants",
        "cta": ("Start taking orders from your own website", ("Start a free quote", "#quote-form"), ("Food and beverage marketing", "/food-and-beverage-marketing/")),
        "blocks": [
            {"type": "stats", "items": [("Takeout", "Pickup, curbside and delivery options"), ("Your website", "Orders come to you, not a marketplace"), ("Your data", "Every guest saved to your CRM"), ("Kitchen view", "Orders tracked from ticket to hand-off")]},
            {"type": "features", "title": "Built for restaurants, cafés, food trucks and bars", "items": [
                ("Menu on your site", "Your full menu with photos, descriptions, sizes, modifiers and add-ons, easy to update when prices or specials change."),
                ("Takeout, pickup and delivery", "Guests choose pickup, curbside or delivery and a ready time. You control the hours and lead times."),
                ("Order tracking", "Every order lands in the platform so the kitchen can see what is due and mark it ready."),
                ("Guest updates by text", "Confirmation and ready-for-pickup messages go out automatically so nobody is waiting at the counter."),
                ("Payments connected to your POS", "Card payments through gateways like Square and Stripe, with the money going to you."),
                ("Guests in your CRM", "Each order creates or updates a guest record, so you can invite them back with email and SMS."),
            ]},
            {"type": "steps", "title": "How an order flows", "items": [
                ("Guest orders", "From the menu on your website, on any device, with pickup or delivery selected."),
                ("Kitchen gets the ticket", "The order appears in your platform with the requested time."),
                ("Guest is notified", "An automatic text confirms the order and says when it is ready."),
                ("Review request", "After the order, the platform asks the guest for a Google review."),
            ]},
            {"type": "compare", "title": "Ordering on your website versus third-party apps", "cols": ("Your website", "Third-party apps"), "rows": [
                ("Customer relationship", "Yours, saved to your CRM", "Theirs, hidden from you"),
                ("Marketplace commission", "None. Orders come through your own site", "A cut of every order"),
                ("Branding", "Your menu, your photos, your name", "One listing among competitors"),
                ("Menu control", "Change items, prices and hours instantly", "Wait on the marketplace"),
                ("Repeat business", "Email and SMS campaigns to past guests", "You cannot contact them"),
            ]},
            {"type": "portfolio", "title": "Restaurant websites we have built", "cat": "Restaurant"},
            {"type": "quote", **QUOTE_BROTHERS},
            {"type": "related", "title": "Everything a restaurant needs online", "items": [
                ("Food & Beverage Marketing", "Get found for 'near me' searches, keep listings and reviews current, and fill tables.", "/food-and-beverage-marketing/"),
                ("Merchant Services", "Fast, secure card payments for online and in-person orders.", "/merchant-services/"),
                ("Automated Email & SMS", "Announce specials and events to guests who have ordered before.", "/automated-email-and-sms/"),
            ]},
            {"type": "faq", "title": "Online ordering questions", "items": [
                ("Can I set different hours for pickup and delivery?", "Yes. Ordering hours, lead times and pickup versus delivery availability are set per option."),
                ("How do I update the menu?", "From your platform. Items, prices, photos and daily specials update instantly on your website."),
                ("Do I need new hardware?", "No. Orders are viewed on any phone, tablet or computer, and card payments run through your existing gateway."),
                ("What about catering or large orders?", "Catering inquiries can run through a quote form, be tracked on the calendar and be invoiced from the same platform."),
            ] + faq_common("Online ordering")},
            FORM,
        ],
    },
}

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
RUN = {
    "/integrated-inbox/": {
        "cta": ("Every conversation in one place", ("Start a free quote", "#quote-form"), ("Explore the platform", "/run/")),
        "blocks": [
            {"type": "stats", "items": [("One inbox", "Email, text and web leads together"), ("Two-way SMS", "Text customers from the platform"), ("Real time", "Notifications on every device"), ("History", "Every conversation on the contact record")]},
            {"type": "features", "title": "What lands in your integrated inbox", "items": [
                ("Website leads", "Quote requests, booking requests and contact forms from your site."),
                ("Two-way text messages", "Reply to customers by SMS from your desk or the app, with the thread saved to the contact."),
                ("Email", "Customer email in the same view as texts and web leads, so nothing is missed."),
                ("Booking requests", "Appointment requests to confirm with one tap, straight onto your calendar."),
                ("Review alerts", "New reviews appear alongside your messages so you can respond quickly."),
                ("Team visibility", "Everyone on your team sees the same conversations and who replied."),
            ]},
            {"type": "split", "title": "Respond faster, win more jobs", "photo": "support", "checks": ["Real-time notifications on phone and desktop", "Saved replies for common questions", "Conversation history on every contact record", "Attach estimates and invoices to a reply", "Security and privacy built in"], "cta": ("See the CRM", "/cloud-based-crm/")},
            {"type": "quote", **QUOTE_ERIC},
            {"type": "faq", "title": "Inbox questions", "items": [
                ("Can customers text my business number?", "Yes. Two-way SMS runs through the platform so texts arrive in the inbox and replies come from your business."),
                ("Does it work on my phone?", "Yes. The Charlie Company Business Platform app puts the full inbox on iOS and Android."),
                ("Can more than one person use it?", "Yes. Your team shares the inbox and every reply is attributed."),
            ] + faq_common("The integrated inbox")},
            APP,
        ],
    },
    "/integrated-calendar/": {
        "cta": ("Let customers book while you work", ("Start a free quote", "#quote-form"), ("Explore the platform", "/run/")),
        "blocks": [
            {"type": "stats", "items": [("24/7", "Online booking from your website"), ("Live", "Real-time availability"), ("Fewer no-shows", "Automated confirmations and reminders"), ("One view", "Jobs, appointments and events together")]},
            {"type": "features", "title": "What the integrated calendar does", "items": [
                ("Online appointment scheduling", "Customers pick a service and a time from your website, day or night, without the back-and-forth."),
                ("Real-time availability", "Only open slots are shown, so double bookings do not happen."),
                ("Confirmations and reminders", "Automatic email and text confirmations and reminders cut no-shows and last-minute cancellations."),
                ("Team scheduling", "Assign appointments to crew members and see everyone's day at a glance."),
                ("Job and event tracking", "Estimates, installs, catering events and follow-ups all live on the same calendar."),
                ("Sync with your phone", "Manage the schedule from the app wherever the day takes you."),
            ]},
            {"type": "steps", "title": "How online booking works", "items": [
                ("Customer picks a service", "Services, durations and buffer times are set up once."),
                ("Chooses a time", "From your live availability, on any device."),
                ("Gets confirmed", "Confirmation and reminders go out automatically."),
                ("You see it instantly", "The booking sits on your calendar and in your inbox, and the contact is in your CRM."),
            ]},
            {"type": "quote", **QUOTE_AMBER},
            {"type": "faq", "title": "Calendar questions", "items": [
                ("Can I approve bookings before they are confirmed?", "Yes. Choose instant booking or request-and-confirm for each service."),
                ("Can customers pay when they book?", "Yes. Deposits or full payment can be collected at booking through your merchant services."),
                ("Does it handle recurring appointments?", "Yes. Maintenance visits, lessons and standing appointments can repeat automatically."),
            ] + faq_common("The integrated calendar")},
            APP,
        ],
    },
    "/estimate-invoice-and-billing/": {
        "cta": ("Quote it, invoice it, get paid", ("Start a free quote", "#quote-form"), ("Explore the platform", "/run/")),
        "blocks": [
            {"type": "stats", "items": [("Minutes", "To send a professional estimate"), ("One tap", "Estimate becomes an invoice"), ("Card payments", "Secure, from the invoice itself"), ("$1.4M+", "Collected by one roofing client through the platform")]},
            {"type": "features", "title": "Estimates, invoices and billing in one flow", "items": [
                ("Effortless estimates", "Build accurate, itemized quotes in minutes from saved services and prices, and send them from the job site."),
                ("Instant invoicing", "Convert an accepted estimate to an invoice with itemization, taxes and payment terms already filled in."),
                ("Secure card payments", "Customers pay online from the invoice with an integrated payment gateway, no third-party processor to juggle."),
                ("Deposits and progress billing", "Collect a deposit up front and bill the balance on completion."),
                ("Automatic reminders", "Overdue invoices get a friendly reminder without you chasing anyone."),
                ("Client records", "Every estimate, invoice and payment is stored on the customer's contact record."),
            ]},
            {"type": "steps", "title": "From walkthrough to paid", "items": [
                ("Estimate on site", "Itemize the job on your phone and send it before you leave the driveway."),
                ("Customer approves", "One tap to accept, with the approval logged."),
                ("Invoice goes out", "The estimate becomes the invoice, sent by email or text."),
                ("Payment lands", "Card payment online, with a review request sent once the job is closed."),
            ]},
            {"type": "quote", **QUOTE_PEYTON},
            {"type": "faq", "title": "Billing questions", "items": [
                ("What does it cost to take card payments?", "Merchant services rates are quoted for your business. There is no separate software fee for invoicing."),
                ("Can I add my logo and terms?", "Yes. Estimates and invoices carry your branding, terms and notes."),
                ("Does it work with my accountant?", "Payments, invoices and money collected are reported monthly and can be exported."),
            ] + faq_common("Estimates, invoices and billing")},
            APP,
        ],
    },
    "/cloud-based-crm/": {
        "cta": ("Every customer, every job, one record", ("Start a free quote", "#quote-form"), ("Explore the platform", "/run/")),
        "blocks": [
            {"type": "stats", "items": [("One place", "Leads, contacts and history"), ("Automatic", "Contacts created from every lead"), ("Anywhere", "Cloud-based, on every device"), ("50%", "Growth for one accounting firm after switching")]},
            {"type": "features", "title": "What the CRM keeps track of", "items": [
                ("Leads and contacts", "Every lead from your website, ads, listings and calls becomes a contact automatically, no spreadsheets or sticky notes."),
                ("Customer history", "Messages, appointments, estimates, invoices and payments on one timeline per customer."),
                ("Payment and invoice tracking", "See who owes what and what has been paid, and send reminders from the record."),
                ("Notes, files and documents", "Job notes, photos and signed documents stored with the customer."),
                ("Tags and segments", "Group customers by service, area or status for targeted email and SMS campaigns."),
                ("Pipeline view", "New, quoted, scheduled, completed. Know where every job stands."),
            ]},
            {"type": "split", "title": "Built around how small businesses actually work", "photo": "colleagues", "reverse": True, "checks": ["No training course needed to get started", "Works on phone, tablet and desktop", "Client portal for customers to view invoices and pay", "Secure document sharing", "HIPAA-compliant option for health practitioners"], "cta": ("Read a case study", "/case-studies/perkins-tax-accounting/")},
            {"type": "quote", **QUOTE_ASHLEY},
            {"type": "faq", "title": "CRM questions", "items": [
                ("Can I import my existing customers?", "Yes. Your onboarding team imports your customer list so you start with a full database."),
                ("Is my data secure?", "Yes. Data is stored in the cloud with access controls, and a HIPAA-compliant configuration is available for health practices."),
                ("Can my customers log in?", "Yes. The client portal lets customers view invoices, make payments and upload documents."),
            ] + faq_common("The cloud-based CRM")},
            APP,
        ],
    },
    "/automated-email-and-sms/": {
        "cta": ("Follow up with every lead automatically", ("Start a free quote", "#quote-form"), ("Explore the platform", "/run/")),
        "blocks": [
            {"type": "stats", "items": [("Automatic", "Triggered by what the customer does"), ("Email + SMS", "Both channels from one platform"), ("Personal", "Every message uses the customer's details"), ("Segments", "Send to the right group, not everyone")]},
            {"type": "features", "title": "Campaigns that run themselves", "items": [
                ("New lead follow-up", "A thank-you and next step goes out the moment a lead comes in, before your competitor calls back."),
                ("Appointment reminders", "Confirmation, reminder and running-late messages by text so no-shows drop."),
                ("Review requests", "After every completed job, a request for a Google review with a direct link."),
                ("Seasonal campaigns", "Tune-up reminders, holiday specials and event announcements sent to the right segment."),
                ("Re-engagement", "Customers you have not heard from in a while get a nudge with an offer."),
                ("Two-way texting", "Replies land in your integrated inbox so a campaign becomes a conversation."),
            ]},
            {"type": "steps", "title": "Setting up a campaign", "items": [
                ("Pick a trigger", "New lead, booking, completed job, or a date such as the start of cooling season."),
                ("Choose the audience", "Everyone, or a segment by service, area or status."),
                ("Personalize the message", "Templates filled with the customer's name, service and details."),
                ("Let it run", "Messages send on schedule and results show in your monthly report."),
            ]},
            {"type": "quote", **QUOTE_SHARON},
            {"type": "faq", "title": "Email and SMS questions", "items": [
                ("Do customers have to opt in?", "Yes. Contacts collected through your site and platform include consent, and every message carries an opt-out."),
                ("Can I write my own messages?", "Yes. Use the templates or write your own, and your team can help."),
                ("How is this different from a newsletter tool?", "It is tied to your CRM and calendar, so messages trigger from real events like a booking or a finished job."),
            ] + faq_common("Automated email and SMS")},
            APP,
        ],
    },
    "/merchant-services/": {
        "cta": ("Get paid faster, from anywhere", ("Start a free quote", "#quote-form"), ("Explore the platform", "/run/")),
        "blocks": [
            {"type": "stats", "items": [("Faster", "Access to your funds"), ("Secure", "Card payments from invoices and bookings"), ("Flexible", "Card, online and in person"), ("Connected", "Payments logged to the customer record")]},
            {"type": "features", "title": "How merchant services work with your platform", "items": [
                ("Pay from the invoice", "Customers pay by card from the invoice link, on any device, and the payment posts to the record."),
                ("Deposits at booking", "Collect a deposit or full payment when an appointment is booked online."),
                ("Online ordering and ecommerce", "The same processing behind your online ordering menu or product store."),
                ("Gateway integration", "Connect to your point of sale through gateways like Square and Stripe."),
                ("Fast funding", "Improve cash flow with faster fund transfers to your bank."),
                ("Reporting", "Money collected is part of your monthly report and visible in the platform any time."),
            ]},
            {"type": "quote", **QUOTE_PEYTON},
            {"type": "faq", "title": "Payment questions", "items": [
                ("What are the rates?", "Rates are quoted for your business based on volume and card mix. Ask your team for a quote."),
                ("Can I take payments in the field?", "Yes. Send the invoice from your phone and the customer pays on theirs, or take the card on the spot in the app."),
                ("Is it secure?", "Payments run through a PCI-compliant gateway. Card details are never stored on your device."),
            ] + faq_common("Merchant services")},
            APP,
        ],
    },
    "/business-domains/": {
        "cta": ("Secure your business name online", ("Start a free quote", "#quote-form"), ("Website design", "/website-design/")),
        "blocks": [
            {"type": "stats", "items": [("Your name", "Registered to your business"), ("SSL", "Security certificate included"), ("Connected", "Pointed at your site and email"), ("Managed", "Renewals handled so it never lapses")]},
            {"type": "features", "title": "What domain management covers", "items": [
                ("Expert guidance", "Help choosing a memorable domain that matches your business name and trade."),
                ("Registration in your name", "The domain is registered to your business, so you own it."),
                ("Seamless integration", "Connected to your website and business email without you touching a DNS record."),
                ("SSL security", "A certificate so your site shows the padlock and customer data is encrypted."),
                ("Renewals handled", "We track renewal dates so your site never goes dark."),
                ("Ongoing support", "Transfers, additional domains and redirects handled by your team."),
            ]},
            {"type": "source", "match": r"The Process: Getting Your Domain"},
            {"type": "faq", "title": "Domain questions", "items": [
                ("I already have a domain. Can I keep it?", "Yes. We can point your existing domain at your new site or transfer it so everything is managed together."),
                ("Do I own the domain?", "Yes. It is registered to your business."),
                ("Can I buy extra domains for campaigns?", "Yes. Additional domains can be registered and redirected to your main site."),
            ] + faq_common("Domain management")},
        ],
    },
    "/business-email-management/": {
        "cta": ("Email that matches your business name", ("Start a free quote", "#quote-form"), ("Business domains", "/business-domains/")),
        "blocks": [
            {"type": "stats", "items": [("you@yourbusiness", "Addresses on your own domain"), ("Every employee", "An account for each team member"), ("Secure", "Spam filtering, encryption and two-factor"), ("Backed up", "Regular backups and recovery")]},
            {"type": "features", "title": "What business email management includes", "items": [
                ("Custom addresses", "Professional addresses on your domain for you and each employee, plus shared addresses like info@ or service@."),
                ("Setup on every device", "Phones, tablets and computers configured so mail works everywhere."),
                ("Security", "Spam filters, encryption and two-factor authentication protecting your accounts."),
                ("Backup and recovery", "Regular backups so a lost device or deleted folder is not a lost conversation."),
                ("Staff changes", "New hires set up and departing staff offboarded with mail forwarded where it belongs."),
                ("Integrated inbox", "Customer email flows into your platform inbox alongside texts and web leads."),
            ]},
            {"type": "faq", "title": "Email questions", "items": [
                ("Can I keep my Gmail?", "Yes. Your custom address can forward to or be added to the mail app you already use."),
                ("How many accounts can I have?", "As many as your team needs. Accounts are added as you hire."),
                ("What happens to email if I switch providers later?", "Your domain and mailboxes belong to your business and can be exported."),
            ] + faq_common("Business email management")},
        ],
    },
    "/ecommerce/": {
        "cta": ("Sell online without a second system", ("Start a free quote", "#quote-form"), ("Explore the platform", "/run/")),
        "blocks": [
            {"type": "stats", "items": [("24/7", "Your store is always open"), ("Integrated", "Orders in the same platform as everything else"), ("Secure", "Card payments through your merchant account"), ("Tracked", "Sales in your monthly report")]},
            {"type": "features", "title": "What the ecommerce platform includes", "items": [
                ("Product catalog", "Products, variants, photos and inventory managed from your platform."),
                ("Secure checkout", "Card payments through your merchant services with the money going to you."),
                ("Order management", "Orders, fulfillment status and customer details in one view."),
                ("Customers in your CRM", "Every buyer becomes a contact you can follow up with by email or SMS."),
                ("Sales tracking", "Real-time sales performance without spreadsheets."),
                ("Part of your website", "The store lives on your own site, matched to your brand and found by search."),
            ]},
            {"type": "related", "title": "Also for businesses that sell", "items": [
                ("Online Ordering", "Takeout, pickup and delivery for restaurants and cafés.", "/online-ordering/"),
                ("Merchant Services", "Fast, secure processing behind every sale.", "/merchant-services/"),
                ("Automated Email & SMS", "Bring customers back with offers and new arrivals.", "/automated-email-and-sms/"),
            ]},
            {"type": "faq", "title": "Ecommerce questions", "items": [
                ("Can I sell services and gift cards?", "Yes. Physical products, services, packages and gift cards can all be sold online."),
                ("Do I need my own payment processor?", "No. Payments run through merchant services included with the platform."),
                ("Can I ship and offer local pickup?", "Yes. Shipping options and local pickup are configured per store."),
            ] + faq_common("The ecommerce platform")},
            APP,
        ],
    },
}

# ---------------------------------------------------------------------------
# Industries
# ---------------------------------------------------------------------------
def cap(name: str) -> str:
    return name if not name.islower() else name[0].upper() + name[1:]


def industry(name: str, *, stats, includes, pages, photo, portfolio, quote, faq, cta, split_title, pain=None, titles=None):
    t = {"includes": f"What your {name} campaign includes", "pages": f"Service pages we write for {name} companies",
         "portfolio": f"{cap(name)} websites we have built", "faq": f"{cap(name)} marketing questions", **(titles or {})}
    blocks = [
        {"type": "stats", "items": stats},
        {"type": "features", "title": t["includes"], "items": includes},
        {"type": "split", "title": split_title, "photo": photo, "reverse": True, "checks": pain or [], "cta": ("See pricing", "/pricing/")} if pain else None,
        {"type": "chips", "title": t["pages"], "items": pages},
        {"type": "portfolio", "title": t["portfolio"], "cat": portfolio} if portfolio else None,
        {"type": "quote", **quote} if quote else None,
        {"type": "faq", "title": t["faq"], "items": faq + faq_common("Every plan")},
        FORM,
    ]
    return {"cta": cta, "blocks": [b for b in blocks if b]}


INDUSTRIES = {
    "/hvac-marketing/": industry("HVAC",
        stats=[("Millions", "HVAC searches on Google every month"), ("24/7", "Online booking for emergency calls"), ("Seasonal", "Tune-up campaigns by email and SMS"), ("No contracts", "Month to month")],
        includes=[
            ("A website built for HVAC", "Pages for AC repair, furnace installation, maintenance plans and emergency service, with click-to-call on every screen."),
            ("Search Everywhere Optimization", "Rank for 'AC repair near me' and 'furnace not working' across Google, maps, directories and AI answers."),
            ("Listings and Google Business Profile", "Accurate hours, service areas and categories so emergency searches find a technician, not a wrong number."),
            ("Review requests after every job", "A text after each service call asking for a Google review, so your rating keeps climbing."),
            ("Online scheduling", "Customers book tune-ups and estimates from your site while your team is on a roof."),
            ("Estimates and invoices from the truck", "Quote a replacement system on site, collect a deposit and invoice the balance on completion."),
        ],
        pain=["Emergency calls at night going to voicemail", "Slow seasons with no campaign to fill them", "Maintenance plans nobody knows you offer", "Five-star jobs that never turn into reviews"],
        split_title="Built for how HVAC customers buy",
        pages=["AC repair", "AC installation", "Furnace repair", "Furnace installation", "Heat pumps", "Ductless mini-splits", "Duct cleaning", "Indoor air quality", "Maintenance plans", "Emergency HVAC", "Commercial HVAC", "Thermostats"],
        photo="actech", portfolio="HVAC", quote=QUOTE_POHLMAN, cta=("Land more of the HVAC jobs you want", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        faq=[("Can you promote maintenance plans?", "Yes. A maintenance plan page, seasonal email and SMS reminders and a booking link make plans easy to sell and renew."),
             ("Do you handle both residential and commercial?", "Yes. Separate pages and campaigns for residential and commercial work so each audience finds the right message."),
             ("How do you handle emergency calls?", "Click-to-call on every page, after-hours booking and text alerts to your on-call tech.")]),
    "/plumbing-marketing/": industry("plumbing",
        stats=[("97%", "Go online when they need a plumber fast"), ("93%", "Use a search engine to find a local one"), ("24/7", "Booking for emergencies"), ("No contracts", "Month to month")],
        includes=[
            ("A plumbing website that converts", "Pages for drain cleaning, water heaters, leak repair and emergency plumbing, each with a call button and quote form."),
            ("Search Everywhere Optimization", "Show up for 'plumber near me', 'water heater replacement' and every town you serve."),
            ("Listings that get the call", "Consistent name, phone and hours across Google, Apple, Yelp and the directories people check in a hurry."),
            ("Reviews on autopilot", "A review request after every finished job, and alerts when a new review posts."),
            ("Online booking and dispatch", "Non-emergency jobs booked from the site and assigned to a tech on the calendar."),
            ("Quote, invoice, get paid", "Itemized estimates on site, invoices by text and card payment before you leave."),
        ],
        pain=["Emergency searches finding a competitor first", "Wrong phone numbers on old directory listings", "No follow-up on unsold water heater quotes", "Great work that never becomes a review"],
        split_title="Built for how plumbing customers buy",
        pages=["Emergency plumbing", "Drain cleaning", "Water heater repair", "Water heater installation", "Leak detection", "Sewer line repair", "Repiping", "Garbage disposals", "Fixture installation", "Backflow testing", "Commercial plumbing", "Gas lines"],
        photo="plumbing", portfolio="Water Services", quote=QUOTE_POHLMAN, cta=("Be the plumber they find first", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        faq=[("How fast can emergency pages rank?", "Emergency and near-me pages are prioritized in the build and indexed within weeks. Listings and reviews accelerate the climb."),
             ("Can customers book online for non-emergencies?", "Yes. Drain cleaning, inspections and installs can be booked from your site straight onto the calendar."),
             ("Do you cover multiple service areas?", "Yes. A page for every town you serve, so you compete locally in each one.")]),
    "/roofing-marketing/": industry("roofing",
        stats=[("85%+", "Of consumers search for roofers online"), ("$1.4M+", "Collected by Top Roofing through our platform"), ("Storm-ready", "Campaigns that launch when weather hits"), ("No contracts", "Month to month")],
        includes=[
            ("A roofing website built to close", "Pages for roof replacement, repair, storm damage and inspections, with financing and a free-inspection form."),
            ("Search Everywhere Optimization", "Own 'roofing company near me', 'roof repair' and every neighborhood you work, in Google, maps and AI answers."),
            ("Storm response campaigns", "Email, SMS and ads ready to go when hail or wind moves through your area."),
            ("Reviews and project photos", "Review requests after every job and finished roofs posted to your site and social page."),
            ("Inspection scheduling", "Homeowners book a free inspection online, with reminders that keep the appointment."),
            ("Estimates, deposits and invoices", "Detailed estimates from the driveway, deposits collected online and final invoices paid by card."),
        ],
        pain=["Storm season traffic going to out-of-town chasers", "Leads that go cold waiting on an estimate", "A portfolio of great roofs nobody can see online", "Insurance-claim questions with no page answering them"],
        split_title="Built for how roofing customers buy",
        pages=["Roof replacement", "Roof repair", "Storm damage", "Hail damage", "Insurance claims", "Roof inspections", "Metal roofing", "Shingle roofing", "Flat and commercial roofing", "Gutters", "Siding", "Financing"],
        photo="roofing", portfolio="Home Services", quote=QUOTE_PEYTON, cta=("More roofs, fewer chasers", ("Get a free quote", "#quote-form"), ("Read the Top Roofing case study", "/case-studies/top-roofing-and-contracting/")),
        faq=[("Can you help with insurance-claim work?", "Yes. Storm damage and insurance claim pages explain the process and capture the homeowner while the damage is fresh."),
             ("Do you post our finished roofs?", "Yes. Send photos from the job and our team turns them into website galleries and social posts."),
             ("How quickly can a storm campaign launch?", "Templates are prepared in advance so email, SMS and ads can go out the day a storm passes.")]),
    "/home-remodeling-marketing/": industry("home remodeling",
        stats=[("90%+", "Of homeowners start remodeling searches online"), ("Gallery", "Project photos that sell the next job"), ("Consult", "Booked online in a few clicks"), ("No contracts", "Month to month")],
        includes=[
            ("A remodeling website that shows your work", "Kitchen, bath, basement and addition pages built around before-and-after galleries."),
            ("Search Everywhere Optimization", "Rank for 'kitchen remodel', 'bathroom remodeler near me' and the towns you serve."),
            ("Design consultation booking", "Homeowners book a consultation from your site and get automatic reminders."),
            ("Reviews and referrals", "Review requests when the project wraps, and email campaigns that keep past clients referring."),
            ("Estimates and progress billing", "Detailed estimates, deposits and milestone invoices paid online."),
            ("Social proof on social", "Project reveals and client reviews posted to your page twice a week."),
        ],
        pain=["Big-ticket leads that never hear back fast enough", "Photos of finished kitchens sitting on a phone", "Consultation no-shows", "Seasonal slowdowns with no pipeline"],
        split_title="Built for how remodeling customers buy",
        pages=["Kitchen remodeling", "Bathroom remodeling", "Basement finishing", "Home additions", "Whole-home remodels", "Outdoor living", "Cabinets and countertops", "Flooring", "Aging-in-place", "Design-build", "Financing", "Our process"],
        photo="remodel", portfolio="Home Services", quote=QUOTE_DAVID, cta=("Land the best remodeling jobs in your area", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        faq=[("Do you build project galleries?", "Yes. Galleries by project type, with before-and-after photos, are part of the site."),
             ("Can leads book a consultation online?", "Yes. Consultations are booked from the site onto your calendar, with reminders sent automatically."),
             ("How do you handle long sales cycles?", "Automated email follow-up keeps a homeowner engaged from the first inquiry to the signed contract.")]),
    "/tree-service-marketing/": industry("tree service",
        stats=[("Millions", "Search monthly for trimming, removal and stump grinding"), ("Storm", "Emergency campaigns ready when weather hits"), ("Reviews", "Requested after every job"), ("No contracts", "Month to month")],
        includes=[
            ("A tree service website", "Pages for tree removal, trimming, stump grinding and emergency storm cleanup with a quote form on every one."),
            ("Search Everywhere Optimization", "Rank for 'tree removal near me' and 'emergency tree service' across Google, maps and AI answers."),
            ("Storm cleanup campaigns", "Email, SMS and social posts that go out the moment a storm hits your service area."),
            ("Listings and reviews", "Accurate directory listings and a review request after every job so referrals happen online."),
            ("Estimate scheduling", "Homeowners request an on-site estimate from your website and it lands on your calendar."),
            ("Invoices from the truck", "Quote, invoice and collect card payment before the chipper is loaded."),
        ],
        pain=["Storm calls going to whoever ranks first that morning", "Quotes that never get followed up", "Neighbors who need you but cannot find you online", "Reviews that live only on word of mouth"],
        split_title="Built for how tree service customers buy",
        pages=["Tree removal", "Tree trimming and pruning", "Stump grinding", "Emergency tree service", "Storm damage cleanup", "Lot clearing", "Tree health and disease", "Cabling and bracing", "Arborist consultations", "Commercial tree care", "Firewood and mulch", "Service areas"],
        photo="tree", portfolio="Landscaping", quote=QUOTE_DAVID, cta=("More tree service leads, in every season", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        faq=[("Can you target the neighborhoods with the biggest trees?", "Yes. Service-area pages and ad targeting focus on the towns and zip codes you want more work from."),
             ("How do storm campaigns work?", "Messages and posts are prepared in advance so they can go out the day a storm passes through."),
             ("Do you handle estimate requests?", "Yes. Requests come to your inbox with a text alert, and estimates can be scheduled from the calendar.")]),
    "/food-and-beverage-marketing/": industry("food and beverage",
        stats=[("90%+", "Of guests research a restaurant online first"), ("Mobile", "Most 'near me' searches happen on a phone"), ("Online ordering", "Takeout and delivery on your own site"), ("No contracts", "Month to month")],
        includes=[
            ("A restaurant website that fills tables", "Menu, hours, photos, reservations and online ordering front and center, and fast on a phone."),
            ("Search Everywhere Optimization", "Show up for 'restaurants near me', your cuisine and your neighborhood in Google, maps and AI answers."),
            ("Listings everywhere guests look", "Accurate hours, menu links and photos across Google, Apple Maps, Yelp and delivery directories."),
            ("Online ordering", "Takeout, pickup and delivery from your own website with orders tracked in the kitchen."),
            ("Reviews and social", "Review requests after every order and social posts featuring dishes, specials and events."),
            ("Email and SMS to regulars", "Specials, events and catering offers sent to guests who have ordered before."),
        ],
        pain=["Wrong hours on a listing costing you a Friday night", "Third-party apps taking a cut of every order", "Catering inquiries lost in a busy inbox", "A menu online that is two prices out of date"],
        split_title="Built for how diners choose",
        pages=["Menu", "Online ordering", "Catering", "Private events", "Reservations", "Happy hour and specials", "Brunch", "Food truck schedule", "Gift cards", "Our story", "Locations", "Careers"],
        photo="food", portfolio="Restaurant", quote=QUOTE_BROTHERS, cta=("Attract more guests to your restaurant, café, truck or bar", ("Get a free quote", "#quote-form"), ("Explore online ordering", "/online-ordering/")),
        faq=[("Can you connect ordering to my POS?", "Payments connect through gateways like Square and Stripe, and orders are tracked in your platform."),
             ("Do you handle catering leads?", "Yes. Catering inquiries run through a quote form, are tracked on the calendar and are invoiced from the same platform."),
             ("How often is the menu updated?", "As often as you like. Menu changes are unlimited and go live immediately.")]),
    "/towing-marketing/": industry("towing",
        stats=[("Cash calls", "Direct jobs instead of motor club rates"), ("24/7", "Click-to-call on every page"), ("Repeat", "Customers saved to your CRM"), ("No contracts", "Month to month")],
        includes=[
            ("A towing website built for the roadside", "Big call button, service list and live 'we are open' cues so a stranded driver calls you in seconds."),
            ("Search Everywhere Optimization", "Rank for 'tow truck near me', 'roadside assistance' and every highway exit you cover."),
            ("Listings that ring your phone", "Correct number and 24-hour status on Google, Apple Maps and every directory a driver might open."),
            ("Reviews from every rescue", "A text after each job asking for a Google review, so your rating outranks the motor clubs."),
            ("Dispatch-friendly inbox", "Every call, text and web request logged so dispatch and drivers see the same thing."),
            ("Invoice and get paid roadside", "Card payment from your phone before the car is off the flatbed."),
        ],
        pain=["Motor clubs setting your rates and your schedule", "Drivers finding a competitor first at 2am", "Repeat customers with no way to reach them", "Cash calls you cannot track"],
        split_title="Cut out the middleman",
        pages=["Emergency towing", "Roadside assistance", "Jump starts", "Lockouts", "Flat tire changes", "Fuel delivery", "Winch-outs and recovery", "Flatbed towing", "Motorcycle towing", "Heavy-duty towing", "Accident recovery", "Impound and storage"],
        photo="towing", portfolio="Auto Services", quote=QUOTE_DAVID, cta=("Get more cash calls", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        faq=[("What is a cash call?", "A job that comes straight to you from a driver searching online, at your rate, instead of a motor club dispatch at theirs."),
             ("Can you show we are open 24 hours?", "Yes. Listings, your site and your Google profile all show 24-hour availability where that is true."),
             ("Do you build repeat business?", "Yes. Every customer is saved to your CRM and can receive follow-up and seasonal offers by text.")]),
    "/legal-marketing-service/": industry("legal",
        stats=[("40%+", "Of consumers look online for a lawyer"), ("30%", "Search directory listings for a firm"), ("Consults", "Booked online, confidentially"), ("No contracts", "Month to month")],
        includes=[
            ("A law firm website that earns trust", "Practice-area pages, attorney bios, results and a confidential consultation form."),
            ("Search Everywhere Optimization", "Rank for your practice areas and city across Google, maps, legal directories and AI answers."),
            ("Pay per click", "Put your firm at the top of search results for your areas of practice, paying only for clicks."),
            ("Listings and reviews", "Consistent listings on legal and local directories, and review requests when a matter closes."),
            ("Consultation scheduling", "Prospective clients book a consultation from your site and receive reminders."),
            ("Secure client portal", "Document sharing, invoices and payments in one secure place for clients."),
        ],
        pain=["Prospective clients calling the firm that ranked first", "Directory profiles with an old address", "Consultation no-shows", "Intake handled across sticky notes and email"],
        split_title="Built for how clients choose a firm",
        pages=["Personal injury", "Family law", "Criminal defense", "Estate planning", "Business law", "Real estate law", "Immigration", "Bankruptcy", "Employment law", "DUI defense", "Attorney profiles", "Case results"],
        photo="lawfirm", portfolio="Legal", quote=QUOTE_ASHLEY, cta=("Attract more of the cases you want", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        faq=[("Is intake information kept confidential?", "Yes. Forms, messages and documents run through a secure platform with access limited to your firm."),
             ("Can you write practice-area content?", "Yes. Our team writes practice-area, FAQ and location pages for your review before anything goes live."),
             ("Do you manage legal directory listings?", "Yes. Legal and local directories are kept accurate as part of listing management.")]),
    "/landscaping-marketing/": industry("landscaping",
        stats=[("40%", "Of homeowners with a yard hire pros"), ("80%+", "Of them search online to find one"), ("Seasonal", "Spring and fall campaigns built in"), ("No contracts", "Month to month")],
        includes=[
            ("A landscaping website that shows your work", "Design, installation, maintenance and hardscape pages built around project photos."),
            ("Search Everywhere Optimization", "Rank for 'landscaper near me', 'lawn care' and 'patio installation' in every town you serve."),
            ("Seasonal campaigns", "Spring cleanup, fall leaf removal and snow removal reminders by email and SMS."),
            ("Listings and reviews", "Accurate listings everywhere and review requests when a project wraps."),
            ("Estimate scheduling", "Homeowners request an on-site estimate from your site and it lands on your calendar."),
            ("Recurring billing", "Maintenance contracts invoiced automatically and paid online."),
        ],
        pain=["Spring rush with no way to book it", "Maintenance clients you invoice by hand", "A phone full of finished-patio photos nobody sees", "Reviews that stay in the neighborhood"],
        split_title="Built for how landscaping customers buy",
        pages=["Landscape design", "Landscape installation", "Lawn care and maintenance", "Hardscaping and patios", "Irrigation", "Outdoor lighting", "Retaining walls", "Sod and seeding", "Mulch and planting", "Snow removal", "Commercial landscaping", "Service areas"],
        photo="landscaping", portfolio="Landscaping", quote=QUOTE_DAVID, cta=("Reach more homeowners who need a landscaper", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        faq=[("Can you handle recurring maintenance billing?", "Yes. Maintenance plans are invoiced on schedule and paid by card, with reminders for overdue accounts."),
             ("Do you post our projects?", "Yes. Send photos from the job and they become galleries and social posts."),
             ("Can you market snow removal in winter?", "Yes. Seasonal pages and campaigns switch with the calendar.")]),
    "/general-contracting-marketing/": industry("general contracting",
        stats=[("40%+", "Research contractors in online directories first"), ("Bids", "Estimates that go out the same day"), ("Progress billing", "Deposits and milestones online"), ("No contracts", "Month to month")],
        includes=[
            ("A contractor website that wins bids", "Service pages, project galleries, licenses and insurance, and a project inquiry form."),
            ("Search Everywhere Optimization", "Rank for 'general contractor near me' and the project types and towns you want."),
            ("Directory listings", "Accurate profiles on the directories homeowners use to vet contractors."),
            ("Reviews and referrals", "Review requests at project close and email campaigns that keep past clients referring."),
            ("Project scheduling", "Site visits and consultations booked from your site onto your calendar."),
            ("Estimates and milestone invoices", "Detailed bids, deposits and progress invoices paid by card."),
        ],
        pain=["Bids that lose to whoever responded first", "Directory profiles missing your license and insurance", "Progress payments chased by phone", "Subcontractors and clients in separate email threads"],
        split_title="Built for how homeowners vet contractors",
        pages=["Home additions", "Renovations", "Custom homes", "Commercial construction", "Tenant improvements", "Decks and porches", "Garage construction", "Structural repairs", "Permits and inspections", "Design-build", "Licensing and insurance", "Project gallery"],
        photo="contracting", portfolio="Home Services", quote=QUOTE_PEYTON, cta=("Win more of the projects you bid", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        faq=[("Can you show our licensing and insurance?", "Yes. A dedicated page and directory profiles present credentials the way homeowners look for them."),
             ("Do you support progress billing?", "Yes. Deposits and milestone invoices are sent and paid through the platform."),
             ("Can subcontractors use the platform?", "Yes. Team members can be added so schedules and conversations stay in one place.")]),
    "/local-business-digital-marketing/": industry("local businesses",
        stats=[("24,000+", "Satisfied clients"), ("5,000+", "Five-star Google reviews"), ("76", "Local markets nationwide"), ("No contracts", "Month to month")],
        includes=[
            ("A website built for your trade", "Service, area and FAQ pages written for what you do and where you do it."),
            ("Search Everywhere Optimization", "Get found in Google results, the map pack, directories and AI answers."),
            ("Listings and reviews", "Accurate listings everywhere and a review request after every job."),
            ("Social media and ads", "Managed posting plus targeted social and display advertising when you want to push."),
            ("The business platform", "Inbox, calendar, CRM, estimates, invoices and payments in one place."),
            ("A team that knows your business", "US-based support and a dedicated relationship manager, month to month."),
        ],
        pain=None, split_title="",
        titles={"includes": "What every local business campaign includes", "pages": "Businesses we work with every day", "portfolio": "Local business websites we have built", "faq": "Local business marketing questions"},
        pages=["Salons and spas", "Auto repair and detailing", "Pet care and veterinary", "Boutiques and retail", "Health and wellness", "Fitness studios", "Accounting and tax", "Cleaning services", "Pest control", "Photographers", "Event venues", "Smoke shops"],
        photo="local", portfolio="Boutique / Retail", quote=QUOTE_SHARON, cta=("Grow faster and run smarter", ("Get a free quote", "#quote-form"), ("See who we work with", "/who-we-work-with/")),
        faq=[("My industry is not listed. Can you help?", "Almost certainly. The platform and campaigns are built around your specific services, whatever the trade."),
             ("Do you work with brand-new businesses?", "Yes. Many clients start with us at launch, with a domain, website, listings and reviews built from day one."),
             ("How involved do I need to be?", "An onboarding call and quick approvals. Our team handles the build, content and ongoing work.")]),
}

# ---------------------------------------------------------------------------
# Company and support
# ---------------------------------------------------------------------------
COMPANY = {
    "/phone-support/": {
        "cta": ("Talk to a real person", ("Call (210) 480-6345", "tel:+12104806345"), ("Send a message", "/support/")),
        "blocks": [
            {"type": "stats", "items": [("US-based", "Support team"), ("Mon to Fri", "9:00am to 5:00pm Central"), ("(210) 480-6345", "One number for every question"), ("In-app", "Message us from your platform")]},
            {"type": "features", "title": "What phone support helps with", "items": [
                ("Platform questions", "Inbox, calendar, estimates, invoices, payments and the mobile app."),
                ("Website changes", "Unlimited updates: new services, photos, hours, staff and offers."),
                ("Campaign updates", "Rankings, listings, reviews, social posts and advertising."),
                ("Reporting walkthroughs", "A plain-English explanation of your monthly report and what to do next."),
                ("Billing and account", "Plan changes, invoices and account details."),
                ("Onboarding", "Getting your team set up and your customers imported."),
            ]},
            {"type": "quote", **QUOTE_DAVID},
            {"type": "faq", "title": "Support questions", "items": [
                ("What if I call outside business hours?", "Leave a message or send a note from your platform and the team responds the next business morning."),
                ("Will I talk to the same people?", "Yes. Your relationship manager and support team know your account and your history."),
                ("Is support included?", "Yes. Unlimited US-based support is part of every plan."),
            ]},
        ],
    },
    "/relationship-manager/": {
        "cta": ("One point of contact for your whole account", ("Book a demo", "/book-a-demo/"), ("Talk to support", "/support/")),
        "blocks": [
            {"type": "stats", "items": [("One person", "Who knows your business front to back"), ("Direct", "Phone number and email"), ("Monthly", "Reporting reviews on request"), ("Unlimited", "Changes and optimizations")]},
            {"type": "features", "title": "What your relationship manager does", "items": [
                ("Knows your account", "Your services, service area, goals and history, so you never start from zero."),
                ("Reviews your report", "Walks through rankings, traffic, leads and money collected and recommends next steps."),
                ("Coordinates changes", "Routes website, listing, content and campaign updates to the right team and follows up."),
                ("Plans the season", "Seasonal campaigns, offers and content scheduled ahead of your busy months."),
                ("Helps you use the platform", "Tips and setup for the inbox, calendar, estimates and automations."),
                ("Escalates fast", "A direct line into production, support and billing when something needs attention."),
            ]},
            {"type": "steps", "title": "How the relationship works", "items": [
                ("Onboarding", "Your manager joins the onboarding call and captures what matters to your business."),
                ("Launch", "Confirms the site, listings and platform are set up the way you want."),
                ("Monthly check-ins", "Reporting reviews and recommendations, as often as you want them."),
                ("Ongoing", "Reach out any time by phone, email or from inside your platform."),
            ]},
            {"type": "quote", **QUOTE_AMBER},
        ],
    },
    "/personal-support/": {
        "cta": ("Your business has a team behind it", ("Start your free demo", "/book-a-demo/"), ("See pricing", "/pricing/")),
        "blocks": [
            {"type": "stats", "items": PARTNER_STATS},
            {"type": "features", "title": "What personal support includes", "items": [
                ("US-based customer support", "A team ready to help with your Charlie Company products and services, Monday to Friday, 9 to 5 Central.", "/phone-support/"),
                ("Dedicated relationship manager", "One person who knows your business and reviews your results with you.", "/relationship-manager/"),
                ("Dedicated onboarding specialists", "Guided setup for your site, listings, platform and customer import."),
                ("Unlimited performance optimizations", "Ongoing changes to your site, content and campaigns at no extra charge."),
                ("Monthly reporting and insights", "A clear report every month and someone to explain it.", "/monthly-reporting/"),
                ("Small Business AI Chat", "Answers and drafts inside your platform, included with your plan."),
            ]},
            {"type": "quote", **QUOTE_DAVID},
            {"type": "related", "title": "Get help", "items": [
                ("Phone support", "Call (210) 480-6345, Monday to Friday, 9am to 5pm Central.", "/phone-support/"),
                ("What to expect", "How onboarding, campaign build and reporting work.", "/what-to-expect/"),
                ("FAQ", "Answers to the questions we hear most.", "/frequently-asked-questions/"),
            ]},
        ],
    },
    "/what-to-expect/": {
        "cta": ("Ready to get started?", ("Start a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "stats", "items": [("Onboarding call", "Where every campaign starts"), ("Quality review", "Before anything goes live"), ("Monthly report", "Rankings, traffic, leads and money"), ("Direct line", "Phone and email for your team")]},
            {"type": "steps", "title": "How we build a campaign that works for you", "items": [
                ("Onboarding call", "A personal call to understand your business, goals and market. Campaign creation collects everything needed to build a strategy tailored to you."),
                ("Campaign build", "Design, content, Search Everywhere Optimization and your business management platform are built by our in-house team."),
                ("Quality review", "Before going live, every detail passes through quality control."),
                ("Launch", "Your site is published and submitted to Google, and monthly reporting begins."),
            ]},
            {"type": "features", "title": "Your team", "items": [
                ("Campaign creation", "Collects your services, service area, competitors and goals on the onboarding call."),
                ("Design and content", "Builds your website and writes service, area and FAQ pages."),
                ("Search and listings", "Runs Search Everywhere Optimization, directories and your Google Business Profile."),
                ("Support", "US-based help by phone, email and from inside your platform."),
                ("Relationship manager", "Your single point of contact for the life of the account."),
                ("Reporting", "Prepares your monthly report and reviews it with you."),
            ]},
            {"type": "source", "match": r"Unleash Your Business Superpowers"},
            {"type": "faq", "title": "Getting-started questions", "items": [
                ("How long until my campaign is live?", "Most campaigns move from onboarding call to launch in a few weeks. You approve the site before it goes live."),
                ("What do I need to provide?", "Your services, service area, logo and any photos of your work. Our team writes the content and supplies imagery."),
                ("When do I see the first report?", "The month after launch, then every month, with your team available to walk through it."),
            ] + faq_common("Every plan")},
            APP,
        ],
    },
    "/pricing/": {
        "cta": ("Get a quote built for your business", ("Start a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "source", "match": r"Business Management Platform for Small Town"},
            {"type": "compare", "title": "What is different about a Charlie Company plan", "cols": ("Charlie Company Media", "Typical agency or DIY builder"), "rows": [
                ("Contract", "Month to month", "12-month agreements"),
                ("Changes", "Unlimited, included", "Billed hourly or done yourself"),
                ("Support", "Unlimited, US-based, plus a relationship manager", "Ticket queue or none"),
                ("Reporting", "Monthly report tied to leads and money collected", "Traffic screenshots"),
                ("Business tools", "Inbox, calendar, CRM, invoicing and payments included", "Separate subscriptions"),
            ]},
            {"type": "source", "match": r"^Testimonials"},
            {"type": "faq", "title": "Pricing questions", "items": [
                ("How much does it cost?", "Plans are quoted for your business based on the package, your market and what you need built. Start a free quote or book a demo and you will have a number quickly."),
                ("Is there a setup fee?", "Your quote covers everything: the build, the campaign and the platform. There are no surprise add-ons for changes or support."),
                ("Can I start with one package and add later?", "Yes. Many clients start with Get Found and add the business platform once leads pick up."),
                ("What payment methods do you accept?", "Major credit cards and ACH, billed monthly."),
            ] + faq_common("Every plan")},
        ],
    },
    "/about-us/": {
        "cta": ("Let's build something together", ("Book a demo", "/book-a-demo/"), ("See careers", "/careers/")),
        "blocks": [
            {"type": "stats", "items": PARTNER_STATS},
            {"type": "custom", "key": "values"},
            {"type": "features", "title": "Everything under one roof", "items": [
                ("Website design and content", "In-house designers and writers build service, area and FAQ pages.", "/website-design/"),
                ("Search Everywhere Optimization", "Google, maps, directories and AI answers.", "/search-engine-optimization/"),
                ("Listings, reviews and social", "Accurate everywhere, with reviews and posts handled for you.", "/business-listings/"),
                ("Advertising", "Targeted social and display campaigns in your market.", "/targeted-social-ads/"),
                ("The business platform", "Inbox, calendar, CRM, estimates, invoices and payments.", "/run/"),
                ("Personal support", "US-based support and a dedicated relationship manager.", "/personal-support/"),
            ]},
            {"type": "split", "title": "Lubbock, Texas based, serving 76 markets nationwide", "photo": "team", "checks": ["7720 University Avenue, Lubbock, TX 79423", "Monday to Friday, 9:00am to 5:00pm Central", "(210) 480-6345", "Campaigns running in 30+ states"], "cta": ("See our locations", "/locations/")},
            {"type": "quote", **QUOTE_ASHLEY},
        ],
    },
    "/case-studies/": {
        "cta": ("Your business could be our next success story", ("Book a demo", "/book-a-demo/"), ("See pricing", "/pricing/")),
        "blocks": [
            {"type": "stats", "items": [("$1.4M+", "Collected by Top Roofing through the platform"), ("50%", "Business growth at Perkins Tax & Accounting"), ("Zero", "No-shows at Holistic Hounds since launch"), ("Half", "The admin time Amber Moon Studios used to spend")]},
        ],
    },
    "/who-we-work-with/": {
        "cta": ("Do not see your industry? We build for it anyway", ("Get a free quote", "#quote-form"), ("Book a demo", "/book-a-demo/")),
        "blocks": [
            {"type": "industries", "title": "Marketing built for your trade"},
            {"type": "stats", "items": PARTNER_STATS},
            {"type": "chips", "title": "Also in our portfolio", "items": ["Auto detailing", "Boutiques and retail", "Health and wellness", "Pet care", "Spas and salons", "Event venues", "Fitness studios", "Accounting and tax", "Smoke shops", "Water services", "Outdoor and travel", "Cleaning services"]},
        ],
    },
}

PAGES = {**GROW, **RUN, **INDUSTRIES, **COMPANY}

# Project pages: what a build in each category includes
PROJECT_INCLUDES = {
    "hvac": {"industry": ("/hvac-marketing/", "HVAC marketing"), "items": [
        ("Emergency call button", "Click-to-call fixed on every screen for after-hours breakdowns."),
        ("Service pages", "AC repair, installation, furnace, heat pumps, duct cleaning and maintenance plans."),
        ("Service-area pages", "A page for every town the company serves."),
        ("Online scheduling", "Tune-ups and estimates booked straight onto the calendar."),
        ("Reviews and financing", "Live Google reviews and a financing page that closes replacements."),
        ("Seasonal campaigns", "Email and SMS reminders wired to the CRM."),
    ]},
    "home-services": {"industry": ("/local-business-digital-marketing/", "Home services marketing"), "items": [
        ("Project gallery", "Before-and-after photos that sell the next job."),
        ("Quote request form", "Leads land in the inbox with a text alert."),
        ("Service pages", "Every service the company offers, written to convert."),
        ("Service-area pages", "Local relevance in each town served."),
        ("Reviews", "Five-star reviews pulled onto the site automatically."),
        ("Estimates and invoices", "Connected to the platform so quotes go out the same day."),
    ]},
}

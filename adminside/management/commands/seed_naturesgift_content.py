from django.core.management.base import BaseCommand
from django.utils import timezone

from adminside.models import Destination, Package, PackageCategory, TravelCollection


def html(text):
    return f"<p>{text}</p>"


DESTINATIONS = [
    ("Kenya", "kenya", "The heart of NaturesGift's safari offering, from classic wildlife circuits to remote cultural expeditions."),
    ("Tanzania", "tanzania", "Northern Tanzania safaris covering Tarangire, Ngorongoro, Serengeti, Ndutu and human-history routes."),
    ("Uganda", "uganda", "Primate journeys, gorilla trekking, chimpanzees, Queen Elizabeth National Park and the Pearl of Africa circuit."),
    ("Rwanda", "rwanda", "Refined primate and conservation journeys across Volcanoes National Park, Nyungwe and Akagera."),
]


CATEGORIES = [
    ("Kenya Safaris", "kenya-safaris", "Classic and specialist Kenya safari circuits."),
    ("Tanzania Safaris", "tanzania-safaris", "Migration, calving and northern Tanzania safari routes."),
    ("Uganda Safaris", "uganda-safaris", "Gorilla, chimpanzee and wildlife journeys in Uganda."),
    ("Rwanda Safaris", "rwanda-safaris", "Primate and conservation-led Rwanda expeditions."),
    ("Niche Corner", "niche-corner", "Special-interest safari experiences for focused travelers."),
]


PACKAGES = [
    {
        "name": "Tribal Expedition",
        "slug": "tribal-expedition",
        "destination": "kenya",
        "category": "kenya-safaris",
        "region": "kenya-safari",
        "safari_type": "cultural",
        "duration_days": 11,
        "price_usd": 3880,
        "route_summary": "Northern Kenya cultural and wilderness expedition",
        "best_season": "Jan - Mar 2027",
        "subtitle": "A cultural and wilderness journey into Kenya's less familiar safari landscapes.",
    },
    {
        "name": "Big Cat Diaries",
        "slug": "big-cat-diaries",
        "destination": "kenya",
        "category": "kenya-safaris",
        "region": "kenya-safari",
        "safari_type": "classic",
        "duration_days": 8,
        "price_usd": 6910,
        "route_summary": "Predator-focused Kenya safari with strong wildlife viewing.",
        "subtitle": "Designed for travelers who want time in big-cat country with expert safari guidance.",
    },
    {
        "name": "Photographers Hub",
        "slug": "photographers-hub",
        "destination": "kenya",
        "category": "niche-corner",
        "region": "niche-corner",
        "safari_type": "photographic",
        "duration_days": 10,
        "price_usd": 14790,
        "route_summary": "Specialist photographic safari built around rare sightings and patient field time.",
        "subtitle": "A premium photographic safari for guests who travel with cameras, patience and purpose.",
    },
    {
        "name": "Tusks & Tides",
        "slug": "tusks-tides",
        "destination": "kenya",
        "category": "kenya-safaris",
        "region": "kenya-safari",
        "safari_type": "beach",
        "duration_days": 8,
        "price_usd": 4990,
        "route_summary": "Amboseli, Tsavo and the Kenyan coast.",
        "subtitle": "A bush and beach route linking elephant country with time by the ocean.",
    },
    {
        "name": "Nature's Wilderness",
        "slug": "natures-wilderness",
        "destination": "kenya",
        "category": "kenya-safaris",
        "region": "kenya-safari",
        "safari_type": "classic",
        "duration_days": 9,
        "price_usd": 6405,
        "route_summary": "A classic Kenya wilderness safari circuit.",
        "subtitle": "A balanced wildlife journey for guests who want variety, scenery and safari rhythm.",
    },
    {
        "name": "Wild Frontiers",
        "slug": "wild-frontiers",
        "destination": "kenya",
        "category": "kenya-safaris",
        "region": "kenya-safari",
        "safari_type": "classic",
        "duration_days": 9,
        "price_usd": 5250,
        "route_summary": "Samburu - Ol Pejeta - Lake Naivasha - Maasai Mara.",
        "subtitle": "A route across northern and southern Kenya, from Special Five country to the Mara.",
    },
    {
        "name": "Kenya Ultimate Circuit",
        "slug": "kenya-ultimate-circuit",
        "destination": "kenya",
        "category": "kenya-safaris",
        "region": "kenya-safari",
        "safari_type": "classic",
        "duration_days": 10,
        "price_usd": 6405,
        "route_summary": "Lake Nakuru - Maasai Mara - Naivasha - Amboseli.",
        "subtitle": "A highlights circuit connecting rhinos, open plains, lake country and elephant landscapes.",
    },
    {
        "name": "Beyond The Horizon",
        "slug": "beyond-the-horizon",
        "destination": "kenya",
        "category": "kenya-safaris",
        "region": "kenya-safari",
        "safari_type": "beach",
        "duration_days": 8,
        "price_usd": 4990,
        "route_summary": "Amboseli, Tsavo and coast extension.",
        "subtitle": "A southern Kenya route for guests who want elephants, red-earth wilderness and coastal rest.",
    },
    {
        "name": "Calving Safari",
        "slug": "calving-safari",
        "destination": "tanzania",
        "category": "tanzania-safaris",
        "region": "tanzania-safari",
        "safari_type": "migration",
        "duration_days": 10,
        "price_usd": 9190,
        "route_summary": "Tarangire - Ngorongoro - Ndutu - Serengeti.",
        "best_season": "Late Dec - Apr",
        "subtitle": "A seasonal Tanzania safari focused on wildebeest calving and predator activity.",
    },
    {
        "name": "Tanzania Tales",
        "slug": "tanzania-tales",
        "destination": "tanzania",
        "category": "tanzania-safaris",
        "region": "tanzania-safari",
        "safari_type": "classic",
        "duration_days": 7,
        "price_usd": 6550,
        "route_summary": "Tarangire - Lake Manyara area - Ngorongoro - Central Serengeti.",
        "subtitle": "A compact northern Tanzania safari featuring elephants, crater landscapes and Serengeti cats.",
    },
    {
        "name": "Footprints of Mankind Adventure - Tanzania",
        "slug": "footprints-of-mankind-adventure-tanzania",
        "destination": "tanzania",
        "category": "niche-corner",
        "region": "niche-corner",
        "safari_type": "cultural",
        "duration_days": 8,
        "price_usd": 0,
        "route_summary": "Laetoli, Olduvai Gorge, Lake Natron and northern Tanzania landscapes.",
        "subtitle": "An outdoorsy Tanzania journey connecting nature, geology and the history of human evolution.",
        "price_note": "Available on request",
    },
    {
        "name": "Pearl of Africa Expedition",
        "slug": "pearl-of-africa-expedition",
        "destination": "uganda",
        "category": "uganda-safaris",
        "region": "uganda-safari",
        "safari_type": "primate",
        "duration_days": 10,
        "price_usd": 8590,
        "route_summary": "Chimpanzees, Queen Elizabeth National Park, Kazinga Channel and gorillas.",
        "subtitle": "A Uganda journey from playful chimpanzees to mountain gorilla trekking.",
    },
    {
        "name": "Silverback Quest / Gorilla Trek",
        "slug": "silverback-quest-gorilla-trek",
        "destination": "uganda",
        "category": "uganda-safaris",
        "region": "uganda-safari",
        "safari_type": "primate",
        "duration_days": 5,
        "price_usd": 5490,
        "route_summary": "Entebbe or Maasai Mara connection to Bwindi Impenetrable National Park.",
        "subtitle": "A focused gorilla-trekking extension that can connect smoothly from a Kenya safari.",
    },
    {
        "name": "Rwanda Primate Expedition",
        "slug": "rwanda-primate-expedition",
        "destination": "rwanda",
        "category": "rwanda-safaris",
        "region": "rwanda-safari",
        "safari_type": "primate",
        "duration_days": 7,
        "price_usd": 11160,
        "route_summary": "Nyungwe chimpanzees, Volcanoes gorillas and optional Golden Monkey tracking.",
        "subtitle": "A refined Rwanda primate journey for travelers with one week to spare.",
    },
]


class Command(BaseCommand):
    help = "Seed starter NaturesGift Expeditions destinations, categories and safari packages."

    def handle(self, *args, **options):
        destinations = {}
        for name, slug, description in DESTINATIONS:
            destinations[slug], _ = Destination.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "destination_type": Destination.COUNTRY,
                    "region": "kenya" if slug == "kenya" else "africa",
                    "description": html(description),
                    "is_active": True,
                    "show_in_navigation": True,
                    "is_featured": slug in {"kenya", "tanzania", "uganda", "rwanda"},
                },
            )

        categories = {}
        for index, (name, slug, description) in enumerate(CATEGORIES, start=1):
            categories[slug], _ = PackageCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": description,
                    "display_order": index,
                    "is_active": True,
                    "show_in_navigation": True,
                },
            )

        for index, item in enumerate(PACKAGES, start=1):
            price_usd = item["price_usd"]
            price_note = item.get("price_note") or f"US ${price_usd:,.0f} per person"
            package, _ = Package.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "subtitle": item["subtitle"],
                    "description": html(item["subtitle"]),
                    "region": item["region"],
                    "safari_type": item["safari_type"],
                    "route_summary": item["route_summary"],
                    "best_season": item.get("best_season", ""),
                    "comfort_level": "Tailor-made safari comfort",
                    "group_size_note": "Based on private safari planning unless otherwise stated",
                    "price_note": price_note,
                    "category": categories[item["category"]],
                    "main_destination": destinations[item["destination"]],
                    "duration_days": item["duration_days"],
                    "duration_nights": max(item["duration_days"] - 1, 0),
                    "adult_price": price_usd * 130 if price_usd else 0,
                    "child_price": 0,
                    "highlights": "\n".join([
                        item["route_summary"],
                        "Private planning and expert safari guidance",
                        "Accommodation and logistics confirmed around guest preferences",
                    ]),
                    "inclusions": "<ul><li>Safari planning and route coordination</li><li>Accommodation guidance</li><li>Ground logistics support</li></ul>",
                    "exclusions": "<ul><li>International flights</li><li>Visa or eTA fees</li><li>Personal expenses and travel insurance</li></ul>",
                    "status": Package.PUBLISHED,
                    "is_featured": index <= 8,
                    "home_rank": index,
                    "published_at": timezone.now(),
                    "meta_title": f"{item['name']} | NaturesGift Expeditions",
                    "meta_description": item["subtitle"],
                },
            )
            package.categories.set([categories[item["category"]]])

        collections = {
            "kenya": ["tribal-expedition", "big-cat-diaries", "wild-frontiers", "kenya-ultimate-circuit"],
            "safaris": ["calving-safari", "tanzania-tales", "pearl-of-africa-expedition", "rwanda-primate-expedition"],
            "themes": ["photographers-hub", "footprints-of-mankind-adventure-tanzania", "silverback-quest-gorilla-trek"],
        }
        for order, (section, slugs) in enumerate(collections.items(), start=1):
            collection, _ = TravelCollection.objects.update_or_create(
                slug=f"naturesgift-{section}",
                defaults={
                    "name": {
                        "kenya": "Kenya Safari Highlights",
                        "safaris": "East Africa Safari Circuits",
                        "themes": "Niche Corner Picks",
                    }[section],
                    "section": section,
                    "description": "Starter collection for the NaturesGift website rebuild.",
                    "display_order": order,
                    "is_active": True,
                    "show_in_navigation": True,
                },
            )
            collection.packages.set(Package.objects.filter(slug__in=slugs))

        self.stdout.write(self.style.SUCCESS("Seeded NaturesGift starter content."))

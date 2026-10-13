import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from adminside.models import Destination, Itinerary, ItineraryDay, Package, PackageCategory


LISTING_URL = 'https://naturesgiftexpeditions.com/our-safari-adventures/'
IMAGE_DIR = Path('package_upload_images/naturesgift-safaris')
PRICE_USD_TO_KES = 130


def clean_text(value):
    return ' '.join(str(value or '').split())


def html_paragraph(value):
    return f'<p>{value}</p>' if value else '<p>Source content not published on the safari page.</p>'


def panel_html(detail, heading):
    heading_node = detail.find(['h2', 'h3'], string=lambda value: clean_text(value).lower() == heading.lower())
    if not heading_node:
        return ''
    panel = heading_node.find_parent('div', class_=lambda classes: classes and 'e-con' in classes)
    if not panel:
        return ''
    items = [clean_text(item.get_text(' ', strip=True)) for item in panel.select('li')]
    if items:
        return '<ul>' + ''.join(f'<li>{item}</li>' for item in items) + '</ul>'
    text = clean_text(panel.get_text(' ', strip=True))
    text = re.sub(r'^' + re.escape(heading) + r'\s*', '', text, flags=re.I)
    return html_paragraph(text)


def parse_itinerary(detail):
    days = []
    headings = detail.find_all('h4', string=lambda value: value and re.match(r'^DAY\s+\d+', clean_text(value), re.I))
    for heading in headings:
        label = clean_text(heading.get_text(' ', strip=True))
        match = re.match(r'^DAY\s+([0-9/&\s]+):\s*(.*)$', label, re.I)
        if not match:
            continue
        numbers = [int(value) for value in re.findall(r'\d+', match.group(1))]
        description = ''
        overnight = ''
        meals = ''
        for sibling in heading.find_next_siblings():
            if getattr(sibling, 'name', None) == 'h4':
                break
            if getattr(sibling, 'name', None) != 'p':
                continue
            text = clean_text(sibling.get_text(' ', strip=True))
            if text.lower().startswith('overnight:'):
                overnight_match = re.search(r'Overnight:\s*(.*?)(?:\s+Meals:|$)', text, re.I)
                meals_match = re.search(r'Meals:\s*(.*)$', text, re.I)
                overnight = clean_text(overnight_match.group(1) if overnight_match else '')
                meals = clean_text(meals_match.group(1) if meals_match else '')
            elif not description:
                description = text
        day_number = numbers[0] if numbers else len(days) + 1
        days.append({
            'day_number': day_number,
            'title': f"{match.group(2)}" + (f" (Days {'/'.join(str(number) for number in numbers)})" if len(numbers) > 1 else ''),
            'description': description,
            'overnight': overnight,
            'meals': meals,
        })
    return days


def destination_for(category_slugs, slug, title, route):
    category_slugs = set(category_slugs)
    if 'rwanda-safaris' in category_slugs or (not category_slugs and 'rwanda' in slug):
        return 'rwanda', 'rwanda-safari', 'Rwanda Safaris', 'rwanda-safaris', 'Rwanda'
    if 'uganda-safaris' in category_slugs or (not category_slugs and ('uganda' in slug or 'gorilla' in title.lower())):
        return 'uganda', 'uganda-safari', 'Uganda Safaris', 'uganda-safaris', 'Uganda'
    if 'tanzania-safaris' in category_slugs or (not category_slugs and ('tanzania' in slug or 'tanzania' in title.lower())):
        return 'tanzania', 'tanzania-safari', 'Tanzania Safaris', 'tanzania-safaris', 'Tanzania'
    return 'kenya', 'kenya-safari', 'Kenya Safaris', 'kenya-safaris', 'Kenya'


class Command(BaseCommand):
    help = 'Import the current public NaturesGift safari catalogue into the configured database.'

    def handle(self, *args, **options):
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        session = requests.Session()
        session.headers.update({'User-Agent': 'NaturesGift catalogue importer/1.0'})
        listing_response = session.get(LISTING_URL, timeout=45)
        listing_response.raise_for_status()
        listing = BeautifulSoup(listing_response.text, 'html.parser')

        imported = 0
        for card in listing.select('[data-elementor-type="loop-item"]'):
            detail_url = None
            title = None
            for link in card.select('h2 a'):
                if '/category/' not in link.get('href', ''):
                    title = clean_text(link.get_text(' ', strip=True))
                    detail_url = urljoin(LISTING_URL, link.get('href'))
                    break
            if not detail_url:
                for link in card.select('a'):
                    if 'view trip' in clean_text(link.get_text(' ', strip=True)).lower():
                        detail_url = urljoin(LISTING_URL, link.get('href'))
                        break
            if not detail_url:
                continue

            detail_response = session.get(detail_url, timeout=45)
            detail_response.raise_for_status()
            detail = BeautifulSoup(detail_response.text, 'html.parser')
            title = title or clean_text(detail.find('h1').get_text(' ', strip=True))
            slug = slugify(title)
            route = clean_text(detail.get_text(' ', strip=True))
            category_links = []
            for category_link in card.select('a[href*="/category/"]'):
                category_slug = urlparse(category_link.get('href', '')).path.rstrip('/').split('/')[-1]
                category_label = clean_text(category_link.get_text(' ', strip=True))
                if category_slug and category_slug not in {item[0] for item in category_links}:
                    category_links.append((category_slug, category_label))
            if not category_links:
                for category_link in detail.select('a[href*="/category/"]'):
                    category_slug = urlparse(category_link.get('href', '')).path.rstrip('/').split('/')[-1]
                    category_label = clean_text(category_link.get_text(' ', strip=True))
                    if category_slug and category_slug not in {item[0] for item in category_links}:
                        category_links.append((category_slug, category_label))
            category_slugs = [item[0] for item in category_links]
            destination_slug, region, category_name, category_slug, destination_name = destination_for(category_slugs, slug, title, route)
            destination, _ = Destination.objects.update_or_create(
                slug=destination_slug,
                defaults={
                    'name': destination_name,
                    'destination_type': Destination.COUNTRY,
                    'region': 'kenya' if destination_slug == 'kenya' else 'africa',
                    'description': html_paragraph(f'{destination_name} safari planning with NaturesGift Expeditions.'),
                    'is_active': True,
                    'show_in_navigation': True,
                    'is_featured': True,
                },
            )
            primary_category, _ = PackageCategory.objects.update_or_create(
                slug=category_slug,
                defaults={
                    'name': category_name,
                    'description': f'{category_name} from NaturesGift Expeditions.',
                    'is_active': True,
                    'show_in_navigation': True,
                },
            )
            categories = [primary_category]
            for extra_slug, extra_name in category_links:
                if extra_slug == category_slug:
                    continue
                extra_category, _ = PackageCategory.objects.update_or_create(
                    slug=extra_slug,
                    defaults={
                        'name': extra_name or extra_slug.replace('-', ' ').title(),
                        'description': f'{extra_name or extra_slug.replace("-", " ").title()} from NaturesGift Expeditions.',
                        'is_active': True,
                        'show_in_navigation': True,
                    },
                )
                categories.append(extra_category)

            card_text = clean_text(card.get_text(' ', strip=True))
            price_match = re.search(r'From:\s*US\s*\$\s*([\d,]+(?:\.\d+)?)', card_text, re.I)
            price_usd = int(float(price_match.group(1).replace(',', ''))) if price_match else 0
            price_note = f"US $ {price_match.group(1)} per person" if price_match else 'Available on request'
            duration_match = re.search(r'(\d+)\s*Days', card_text, re.I)
            days = parse_itinerary(detail)
            duration_days = int(duration_match.group(1)) if duration_match else (max(day['day_number'] for day in days) if days else 1)

            intro_heading = detail.find(['h3', 'h2'], string=lambda value: clean_text(value).lower() == 'introduction')
            intro = ''
            if intro_heading:
                intro_node = intro_heading.find_next('p')
                intro = clean_text(intro_node.get_text(' ', strip=True)) if intro_node else ''
            image = card.select_one('img')
            image_url = image.get('src') if image else ''
            image_path = ''
            if image_url:
                image_response = session.get(image_url, timeout=45)
                image_response.raise_for_status()
                extension = Path(urlparse(image_url).path).suffix.lower() or '.jpg'
                if extension not in {'.jpg', '.jpeg', '.png', '.webp'}:
                    extension = '.jpg'
                image_path = IMAGE_DIR / f'{slug}{extension}'
                image_path.write_bytes(image_response.content)

            package, _ = Package.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': title,
                    'subtitle': intro[:280],
                    'description': html_paragraph(intro),
                    'region': region,
                    'safari_type': 'primate' if 'gorilla' in title.lower() or 'primate' in title.lower() else ('migration' if 'migration' in route.lower() or 'calving' in title.lower() else 'classic'),
                    'route_summary': intro[:280],
                    'best_season': '',
                    'comfort_level': 'Tailor-made safari planning',
                    'group_size_note': 'Pricing and travel dates are subject to confirmation.',
                    'price_note': price_note,
                    'category': primary_category,
                    'main_destination': destination,
                    'duration_days': duration_days,
                    'duration_nights': max(duration_days - 1, 0),
                    'adult_price': price_usd * PRICE_USD_TO_KES,
                    'child_price': 0,
                    'highlights': '\n'.join(day['title'] for day in days[:6]),
                    'inclusions': panel_html(detail, 'Includes'),
                    'exclusions': panel_html(detail, 'Excludes'),
                    'source_url': detail_url,
                    'source_image_url': image_url,
                    'status': Package.PUBLISHED,
                    'is_featured': imported < 8,
                    'home_rank': imported + 1,
                    'published_at': timezone.now(),
                    'meta_title': f'{title} | NaturesGift Expeditions',
                    'meta_description': intro[:300],
                },
            )
            package.categories.set(categories)
            itinerary, _ = Itinerary.objects.update_or_create(
                package=package,
                defaults={'title': f'{title} itinerary', 'overview': intro},
            )
            itinerary.days.all().delete()
            for day in days:
                ItineraryDay.objects.create(
                    itinerary=itinerary,
                    day_number=day['day_number'],
                    title=day['title'],
                    description=day['description'],
                )
            imported += 1
            self.stdout.write(self.style.SUCCESS(f'Imported {title} ({len(days)} itinerary entries) -> {image_path or "no image"}'))

        self.stdout.write(self.style.SUCCESS(f'Imported {imported} NaturesGift safari packages.'))

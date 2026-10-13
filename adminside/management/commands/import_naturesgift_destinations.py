from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from adminside.models import Destination


SOURCE_URL = 'https://naturesgiftexpeditions.com/our-destination/'


def clean_text(value):
    return ' '.join(str(value or '').split())


class Command(BaseCommand):
    help = 'Import destination descriptions from the public NaturesGift destinations page.'

    def handle(self, *args, **options):
        response = requests.get(SOURCE_URL, headers={'User-Agent': 'NaturesGift destination importer/1.0'}, timeout=45)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        imported = 0

        for heading in soup.find_all('h2'):
            title = clean_text(heading.get_text(' ', strip=True))
            if not title.lower().startswith('explore '):
                continue
            name = title[len('Explore '):].strip()
            if name.lower() == 'our destinations':
                continue
            slug = slugify(name)
            content_container = heading.find_parent('div', class_=lambda classes: classes and 'e-con' in classes)
            nodes = content_container.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'ol']) if content_container else []
            image_url = ''
            if content_container and content_container.parent:
                image = content_container.parent.select_one('img[src]')
                image_url = image.get('src', '') if image else ''

            content = [f'<h2>{name}</h2>']
            for node in nodes:
                if node.name in {'h3', 'h4'}:
                    text = clean_text(node.get_text(' ', strip=True))
                    if text:
                        content.append(f'<h3>{text}</h3>')
                elif node.name == 'p':
                    text = clean_text(node.get_text(' ', strip=True))
                    if text:
                        content.append(f'<p>{text}</p>')
                else:
                    items = [clean_text(item.get_text(' ', strip=True)) for item in node.select('li')]
                    items = [item for item in items if item]
                    if items:
                        content.append('<ul>' + ''.join(f'<li>{item}</li>' for item in items) + '</ul>')

            description = ''.join(content)
            destination, _ = Destination.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'destination_type': Destination.COUNTRY,
                    'region': 'kenya' if slug == 'kenya' else 'africa',
                    'description': description,
                    'meta_title': f'{name} Safari Destinations | NaturesGift Expeditions',
                    'meta_description': clean_text(' '.join(BeautifulSoup(description, 'html.parser').stripped_strings))[:300],
                    'source_url': SOURCE_URL,
                    'source_image_url': image_url,
                    'is_active': True,
                    'show_in_navigation': True,
                    'is_featured': True,
                },
            )
            imported += 1
            self.stdout.write(self.style.SUCCESS(f'Imported {destination.name} destination content'))

        self.stdout.write(self.style.SUCCESS(f'Imported {imported} NaturesGift destinations.'))

"""
Chunking intelligent pour événements culturels.
"""

from typing import List, Dict, Any
from datetime import datetime
from langchain_core.documents import Document


class EventChunker:
    """Découpe les événements en chunks sémantiques."""

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def normalize_date(self, date_str: str) -> str:
        """Normalise une date ISO en format lisible."""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%d/%m/%Y à %H:%M")
        except:
            return date_str

    def create_chunks(self, events: List[Dict[str, Any]]) -> List[Document]:
        """Crée des chunks optimisés pour chaque événement."""
        documents = []
        
        for event in events:
            uid = event.get('uid', '')
            title = event.get('title_fr', 'Sans titre')
            description = event.get('description_fr', '')
            city = event.get('location_city', '')
            region = event.get('location_region', '')
            address = event.get('location_address', '')
            date_begin = event.get('firstdate_begin', '')
            date_end = event.get('lastdate_end', '')
            keywords = event.get('keywords_fr', [])
            age_min = event.get('age_min', '')
            age_max = event.get('age_max', '')
            free = event.get('free', False)
            
            # Normaliser dates
            date_begin_fmt = self.normalize_date(date_begin) if date_begin else ''
            date_end_fmt = self.normalize_date(date_end) if date_end else ''
            
            # Métadonnées communes
            base_metadata = {
                "event_id": uid,
                "title": title,
                "location_city": city,
                "location_region": region,
                "firstdate_begin": date_begin,
                "lastdate_end": date_end,
                "url": event.get("canonicalurl", ""),
                "latitude": event.get("location_lat", ""),
                "longitude": event.get("location_lon", ""),
            }
            
            # Chunk 1: Titre + Description courte
            desc_short = description[:400] if description else "Pas de description"
            content_main = f"""Événement: {title}
Lieu: {city}, {region}
Date: {date_begin_fmt}
Description: {desc_short}"""
            
            documents.append(Document(
                page_content=content_main,
                metadata={**base_metadata, "chunk_type": "main"}
            ))
            
            # Chunk 2: Informations pratiques
            info_pratiques = f"""Événement: {title} à {city}
Dates: du {date_begin_fmt} au {date_end_fmt}
Adresse: {address if address else city}"""
            
            if age_min or age_max:
                info_pratiques += f"\nÂge: {age_min or '?'}-{age_max or '?'} ans"
            
            info_pratiques += f"\nGratuit: {'Oui' if free else 'Non'}"
            
            if keywords:
                kw_str = ', '.join(keywords[:5]) if isinstance(keywords, list) else keywords
                info_pratiques += f"\nThèmes: {kw_str}"
            
            documents.append(Document(
                page_content=info_pratiques,
                metadata={**base_metadata, "chunk_type": "practical"}
            ))
            
            # Chunk 3: Description complète (si longue)
            if len(description) > 400:
                desc_parts = self._split_text(description, self.chunk_size, self.overlap)
                for i, part in enumerate(desc_parts):
                    content_desc = f"""Événement: {title}
Lieu: {city}
Date: {date_begin_fmt}
Description complète (partie {i+1}): {part}"""
                    
                    documents.append(Document(
                        page_content=content_desc,
                        metadata={**base_metadata, "chunk_type": "description", "part": i}
                    ))
        
        return documents

    def _split_text(self, text: str, size: int, overlap: int) -> List[str]:
        """Découpe un texte en chunks avec overlap."""
        if len(text) <= size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end]
            
            # Trouver le dernier espace pour couper proprement
            if end < len(text):
                last_space = chunk.rfind(' ')
                if last_space > size // 2:
                    end = start + last_space
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
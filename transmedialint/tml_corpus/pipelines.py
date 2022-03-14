
from tml_corpus.models import ArticleEntity, NamedEntity


__entity_fields__ = ('text', 'label')
__art_ent_fields__ = ('article_id', 'entity_id', 'position')


class NERPipeline(object):
    
    def entity_filter(self, ent):
        return ent.label_ not in ('PRODUCT', 'DATE', 'TIME', 'PERCENT', 'MONEY',
            'QUANTITY', 'ORDINAL', 'CARDINAL')

    
    def process_item(self, item, spider):
        
        art_id = item.get('article_id', False)

        doc = item.get('doc')
        
        if doc is None:
            return item
        
        all_entities = [('_'.join((e.text, e.label_)),
            e.text, e.label_, e.start_char)
            for e in filter(self.entity_filter, doc.ents)] 
        
        unique_entities = {ent[0]: dict(zip(__entity_fields__, ent[1:3]))
            for ent in all_entities}
        
        entity_objects = {k: NamedEntity.objects.get_or_create(**v)
            for k, v in unique_entities.items() if len(v['text']) <= 512}
        
        for ent, created in entity_objects.values():
            if created:
                ent.save()
        
        entities = {k: v[0] for k, v in entity_objects.items()}
        
        for ent in all_entities:
            
            art_ent = ArticleEntity(
                **dict(zip(__art_ent_fields__,
                (art_id, entities[ent[0]].id, entities[ent[0]].id,
                ent[-1]))))
            art_ent.save()
            
        return item

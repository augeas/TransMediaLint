
import spacy

from tml_corpus.models import ArticleEntity, NamedEntity


__nlp__ = spacy.load("en_core_web_sm") 


__entity_fields__ = ('text', 'label')
__art_ent_fields__ = ('article', 'entity', 'position')

class NERPipeline(object):
    
    def entity_filter(self, ent):
        return ent.label_ not in ('PRODUCT', 'DATE', 'TIME', 'PERCENT', 'MONEY',
            'QUANTITY', 'ORDINAL', 'CARDINAL')    
    
    def process_item(self, item, spider):
        
        art_id = item.get('article_id', False)
        art_created = item.get('created', False)
        if not (art_id and art_created and item['raw_text']):
            return item
                
        doc = __nlp__(item['raw_text'])
        
        all_entities = [('_'.join((e.text, e.label_)),
            e.text, e.label_, e.start_char)
            for e in filter(self.entity_filter, doc.ents)] 
        
        unique_entities = {ent[0]: dict(zip(__entity_fields__, ent[1:3]))
            for ent in all_entities}
        
        entity_objects = {k: NamedEntity.objects.get_or_create(**v)[0]
            for k, v in unique_entities.items()}
        
        for ent in all_entities:
            
            art_ent = ArticleEntity(
                **dict(zip(__art_ent_fields__,
                (entity_objects[ent[0]].id, art_id, entity_objects[ent[0]].id,
                ent[-1]))))
            art_ent.save()
            
        return item

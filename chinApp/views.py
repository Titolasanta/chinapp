from django.shortcuts import render
from .forms import ChineseTextForm
from googleapiclient.discovery import build
import re
import jieba
from pypinyin import pinyin
import os

# Google Translate setup
APIKEY = os.getenv('GOOGLE_API_KEY')
if not APIKEY:
    raise ValueError("API Key not found. Please set the GOOGLE_API_KEY environment variable.")


service = build('translate', 'v2', developerKey=APIKEY)

def combine_pinyin(data):
    transformed = []
    for entry in data:
        chinese_words = entry['chinese']
        pinyin_syllables = entry['pinyin']
        
        combined_pinyin = []
        pinyin_index = 0

        for word in chinese_words:
            syllable_count = len(word)
            combined = '-'.join(pinyin_syllables[pinyin_index:pinyin_index + syllable_count])
            combined_pinyin.append(combined)
            pinyin_index += syllable_count

        transformed.append([chinese_words,combined_pinyin])
    
    return transformed


# Helper functions (same as before)
def merge_particles(segmented_words):
    merged = []
    skip = False
    for i, word in enumerate(segmented_words):
        if skip:
            skip = False
            continue
        if word in ['的', '了'] and i > 0:
            merged[-1] += word
        else:
            merged.append(word)
    return merged

def translate_full(text):
    result = re.split(r'[.,，： 。]', text.replace('…',''))
    result = [item.strip() for item in result if item.strip()]

    segmented_words = []
    for sentence in result:
        segmented_words.append(merge_particles(jieba.lcut(sentence, use_paddle=True)))

    meaning = []
    to_translate = []

    for sentence, r in zip(segmented_words, result):
        sentence.insert(0, r)
        to_translate.append(sentence)

    translate = service.translations().list(source='zh', target='en', q=segmented_words).execute()['translations']

    for sentence, t in zip(segmented_words, translate):
        t['translatedText'] = t['translatedText'].split('&#39;')
        sentence.pop(0)
        meaning.append(t['translatedText'].pop(1))


    print(meaning)
    translated_words_with_blanks = []

    for sentence, t in zip(segmented_words, translate):
        temp = []
        for w, tran in zip(sentence, t['translatedText']):
            temp.append(tran)
            x = len(w) - 1  # Calculate x as length of item - 1
            if x > 0:
                temp.extend([' '] * x)  # Append blank spaces x times
        translated_words_with_blanks.append(temp)

    # Prepare data for HTML rendering
    pin = []
    for t in result:
        pin.append([item for sublist in pinyin(t) for item in sublist])


    zipped_data = []
    combined_data = [{'chinese': s, 'pinyin': p} for s, p in zip(segmented_words, pin)]
    
    transformedData = combine_pinyin(combined_data)

    for meaning_text,combined in zip( meaning,  transformedData):
        zipped_data.append({
            'meaning' :meaning_text,
            'combined': combined
        })
    return zipped_data

# New view to handle user input
def translation_view(request):
    if request.method == 'POST':
        form = ChineseTextForm(request.POST)
        if form.is_valid():
            # Get the inputted Chinese text
            Text = form.cleaned_data['chinese_text']
            

            zipped_data = translate_full(Text)
            print(zipped_data)
            context = {
                'zipped_data': zipped_data
            }
            return render(request, 'chinApp/translation.html', context)
        else:
            print("Form is not valid:", form.errors)  # Debugging line to see if form is valid
    else:
        form = ChineseTextForm()


    # If GET request, display the form
    return render(request, 'chinApp/translation_form.html', {'form': form})

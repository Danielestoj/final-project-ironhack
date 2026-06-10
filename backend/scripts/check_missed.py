with open('temp_pdf_enemies.txt','r',encoding='utf-8') as f:
    t = f.read()

with open('scripts/check_missed_output.txt','w',encoding='utf-8') as out:
    for name in ['Arpía','Basilisco','Bocón barbotante','Aparición','Azer']:
        idx = t.find(name)
        if idx >= 0:
            snippet = t[max(0,idx-40):idx+300]
            out.write(f'=== {name} ===\n')
            out.write(snippet)
            out.write('\n\n')
        else:
            out.write(f'MISSING: {name}\n')

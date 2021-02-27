from app import app

if __name__ == "__main__":
    # Initialize Characters Dictionary If Empty
    initialize_characters_dictionary = False # Make configurable
    if initialize_characters_dictionary:
        dictionary_entries = []
        for key, value in cleaned_cedict.items():
            dictionary_entries.append(CharactersDictionary(key, value[0], value[1]))
        db.session.add_all(dictionary_entries)
        db.session.commit()
    app.run(debug=True)


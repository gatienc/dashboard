

def to_camel_case(text):
    # Split the text into words
    words = text.split()

    # Capitalize each word
    capitalized_words = [word.capitalize() for word in words]

    # Join the words back into a single string
    camel_case_text = ''.join(capitalized_words)

    return camel_case_text

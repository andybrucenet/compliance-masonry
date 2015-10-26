from slugify import slugify
from yaml import load

import os
import logging
import sys
import re


def load_yaml(filename):
    """ Load a specific yaml file """
    with open(filename, 'r') as yaml_file:
        return load(yaml_file)


def write_markdown(output_path, filename, text):
    """ Write text to a markdown file """
    filename = os.path.join(output_path, filename)
    with open(filename, 'w') as md_file:
        md_file.write(text)


def convert_references(references):
    """ Converts references data to markdown url bullet point. """
    text = ''
    for reference in references:
        text += '\n* [{0}]({1})\n'.format(
            reference['reference_name'], reference['reference_url'])
    return text


def covert_governors(governors):
    """ Converts governors data to markdown url bullet point. """
    text = ''
    for reference in governors:
        text += '\n* [{0}]({1})\n'.format(
            reference['governor_name'], reference['governor_url'])
    return text


def generate_text_narative(narative):
    """ Checks if the narrative is in dict format or in string format.
    If the narrative is in dict format the script converts it to to a
    string """
    text = ''
    if type(narative) == dict:
        for key in sorted(narative):
            text += '{0}. {1} \n '.format(key, narative[key])
    else:
        text = narative
    return text


def build_summary(summary, output_path):
    """ Construct a gitbook summary for the controls """
    text = "# Summary\n\n"
    for section in summary:
            text += '* [{0} {1} - {2}](content/{3}.md)\n'.format(
                section['standard'],
                section['control'],
                section['control_name'],
                section['slug']
            )
    write_markdown(output_path, 'SUMMARY.md', text)
    write_markdown(output_path, 'README.md', text)


def document_page(summary, certification, standard_key, control_key):
    """ Create a new page dict. This item is a dictionary that
    contains the standard and control keys, a slug of the combined key, and the
    name of the control"""
    control_name = certification['standards'][standard_key][control_key]['meta']['name']
    slug = slugify('{0}-{1}'.format(standard_key, control_key))
    return {
        'control': control_key,
        'standard': standard_key,
        'control_name': control_name,
        'slug': slug
    }


def create_content(control):
    """ Generate the markdown text from each `justification` """
    text = ''
    for justification in control.get('justifications', []):
        text += '\n## {0}\n'.format(justification.get('name'))
        text += generate_text_narative(justification.get('narative'))
        references = justification.get('references')
        if references:
            text += '\n### References\n'
            text += convert_references(references)
        governors = justification.get('governors')
        if governors:
            text += '\n### Governors\n'
            text += covert_governors(governors)
        text += "\n--------\n"
    return text


def build_page(page_dict, certification, output_path):
    """ Write a page for the gitbook """
    text = '# {0}'.format(page_dict['control_name'])
    control = certification['standards'][page_dict['standard']][page_dict['control']]
    text += create_content(control)
    file_name = 'content/' + page_dict['slug'] + '.md'
    write_markdown(output_path, file_name, text)


def natural_sort(elements):
    """ Natural sorting algorithms for stings with text and numbers reference:
    stackoverflow.com/questions/4836710/
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(elements, key=alphanum_key)


def convert_certifications(certification_path, output_path):
    """ Convert certification to pages format """
    summary = []
    certification = load_yaml(certification_path)
    for standard_key in natural_sort(certification['standards']):
        for control_key in natural_sort(certification['standards'][standard_key]):
            page_dict = document_page(summary, certification, standard_key, control_key)
            summary.append(page_dict)
            build_page(page_dict, certification, output_path)
    build_summary(summary, output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        logging.error("Correct usage `python renders/certifications_to_pages.py <CERTIFICATION NAME>`")
        sys.exit()
    _, certification = sys.argv
    convert_certifications(
        certification_path="exports/certifications/" + certification + ".yaml",
        output_path="exports/Gitbook"
    )

## global variables...........................................................................................

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""

base = "./base"
model_dir = "/home/common/data/Big_Data/GenAI"
model_path = 'meta-llama/Llama-2-7b-chat-hf'
hf_aut = ""
scene = {"city" : 1, "town" : 1, "urban" : 1, "village" : 3, "rural" : 3, 
         "forest" : 5, "jungle" : 5, "mountain" : 7, "hill" : 7, "sea" : 9, "ocean" : 9, "aqua" : 9, 
         "room" : 11, "house" : 11, "space" : 13, "universe" : 13, "cosmos" : 13}
model_ids = [
        "runwayml/stable-diffusion-v1-5",
        "stabilityai/stable-diffusion-2-1",
    ]

## importing Libraries........................................................................................

# pip install torch torchvision torchaudio streamlit langchain Ipython huggingface_hub PIL re pathlib transformers diffusers['torch']

import sys
import re
import os
import time
import random
from io import BytesIO
from typing import List, Dict, Tuple

import streamlit as st

import torch
import torch.nn as nn

from PIL import Image
from pathlib import Path

from langchain import HuggingFacePipeline
from langchain import PromptTemplate, LLMChain

from IPython.display import clear_output
from IPython.display import Image as IPImage

import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
from diffusers import DPMSolverMultistepScheduler, StableDiffusionImg2ImgPipeline

import warnings
warnings.filterwarnings("ignore")

import logging
logging.getLogger().setLevel(logging.CRITICAL)

## some utilities............................................................................................


def Template(instruction, new_system_prompt = DEFAULT_SYSTEM_PROMPT ):
    SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
    template =  B_INST + SYSTEM_PROMPT + instruction + E_INST
    return template

def split_paragraphs(story_text, max_words_per_paragraph = 150):
    if story_text is None:
        story_text = "a man"
        
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', story_text.strip())

    current_paragraph = ''
    paragraphs = []

    for sentence in sentences:
        current_paragraph += sentence.strip() + ' '

        if len(current_paragraph.split()) > max_words_per_paragraph:
            sentences_in_paragraph = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', current_paragraph.strip())

            current_paragraph = ' '.join(sentences_in_paragraph[:-1]).strip()

            paragraphs.append(current_paragraph)

            current_paragraph = sentence.strip() + ' '

    if current_paragraph:
        paragraphs.append(current_paragraph)

    return paragraphs

## prompt engineering.....................................................................................

system_prompt = "You write long, wonderful and creative stories on provided topic. \
A short description of the story will be provided to you. \
You have to generate a good story which should be based on the provided description"
instruction = "Write a story on the following topic in 2500 words:\n\n {text}"
template_story = Template(instruction, system_prompt)

system_prompt = """You're an expert prompt generator. The prompt generated by you will be fed to a image generation model.  A part of a story will be provided to you and you have to generate a simple prompt that describes the scenario in that part of the story such that the part of the story can be explained in an image generated by the prompt generated by you.
    
    Here are some rules u have to follow while generating the prompts: 
    1. The prompt be strictly less than 70 words.
    2. Don't include special characters other than comma and hyphen and dot.
    3. You just have to describe the scenario not write the whole story.
    4. Always include "A colored cartoon type sketch of," at the start of every prompt.
    5. The very important one, write in crisp and very simple english, don't use complicated words.
    6. Separate the different traits of the scenario with commas.
    7. If you can't understand the story or text, just write whatever you think the situation could be in the text.
    
    Here are some examples on how to generate the prompt:
    
    Example of a story paragraph:
    Once upon a time, in a not-so-distant future, there lived a man named Alex. Alex was an adventurous soul who dreamed of exploring the great \
    unknown: outer space. From a young age, he would gaze up at the stars with wonder, imagining what it would be like to journey among them.
    
    Expected text from you is:
    A colored cartoon type sketch of, a man looking up in the sky at night, sky has stars & moon.
    
    Example story paragraph:
    As the days turned into weeks, Maya forged friendships with the creatures of the jungle. She shared moments of laughter with mischievous monkeys, \
    and learned the ancient wisdom of wise old elephants. Together, they explored hidden caves and winding rivers, each new discovery fueling Maya's sense of wonder.

    Expected prompt from you is:
    A colored cartoon type sketch of, A girl laughing with monkeys, old elephants, hidden caves, winding rivers.
    
    Example of another story paragraph:
    In the heart of a bustling metropolis, where skyscrapers kissed the sky and streets hummed with the \
    rhythm of life, there existed a city like no other. Its streets were a labyrinth of winding alleys and bustling boulevards, \
    lined with towering buildings that reached for the clouds.

    Expected prompt generated from you is:
    A colored cartoon type sketch of, a metropolitan city, high skycrapers, streets, sky with clouds.
    
    Example story paragraph:
    what's up

    Since the paragraph is vague to understand, you can assume that a person is saying what's up to another person, for this the expected \
    prompt generated by you is:
    A colored cartoon type sketch of, two person speaking.
    
    Further rules:

    Please don't generate more than 70 words, this is a must.
    Please note that all the above examples the generated prompts were less than 20 words, you must also generate the prompts strictly less than 70 words.
    
    I just want the prompt from you not the explanation of why you generated that prompt.
    """

instruction = "Generate a prompt less than 70 words for the story paragraph:\n\n {text}"
template_prompt = Template(instruction, system_prompt)

system_prompt = """You're an expert background scenario recognizer. You will be given a scene of a story you have to read that scene and try to recognize the most suitable background or surrounding scenario where the scene is taking place.
    
    You have to give the output ONLY from below options provided.
    
    1. city
    2. village
    3. forest
    4. mountain
    5. sea
    7. room
    6. space

    You should output the backgrounds from these six options only. You must not output any other background which is not listed above.
    If you can't understand the background in the story just output the background as village by default.

    Here are some examples on how to generate the required option:
    
    Example story paragraph:
    In the heart of a bustling metropolis, where skyscrapers kissed the sky and streets hummed with the \
    rhythm of life, there existed a city like no other. Its streets were a labyrinth of winding alleys and bustling boulevards, \
    lined with towering buildings that reached for the clouds.
    
    Expected guess:
    As from the above paragraph we can guess that the surrounding is of city because metropolis and skycrapers are mentioned. \
    Hence the text generated by you is:
    From the story I infer the background scene as city

    Example story paragraph:
    As the days turned into weeks, Maya forged friendships with the creatures of the jungle. She shared moments of laughter with mischievous monkeys, \
    and learned the ancient wisdom of wise old elephants. Together, they explored hidden caves and winding rivers, each new discovery fueling Maya's sense of wonder.
    
    Expected guess:
    As from the above paragraph we can guess that the surrounding is of forest / jungle because of monkeys, rivers and caves. \
    Hence the text generated by you is:
    From the story I infer the background scene as forest

    Example story paragraph:
    Hey man how are you? All good!

    Expected guess:
    Since the location / surrounding can't be guessed because there is no hint present in the paragraph you have to provide the default option which is village.\
    Hence the text generated by you is:
    From the story I infer the background scene as forest
    """

instruction = "Guess the background scene for the story paragraph:\n\n {text}"
template_scene = Template(instruction, system_prompt)

system_prompt = """You're an expert at guessing whether a event is occuring in day or night based on the description of the event.\
You will be given a scene of a story which you have to read. After reading the scene you have to tell whether the scene in the story is taking place in day or in night.
In case you're not able to guess between night or day, then by default output day.

    You must output only one of the following options:
    1. day
    2. night

    You should not output times like: afternoon, morning, evening etc. You have to output only either day or night.
    In case you're not able to guess between night or day, then by default output day.

    Here are some examples on how to generate the required option:
    
    Example story paragraph:
    Once upon a sun-kissed morning, in the heart of a serene village nestled amidst rolling hills and lush greenery, a bustling day began to unfold. \
    The village, with its quaint cottages and winding pathways, exuded an aura of tranquility under the clear blue sky.
    
    Expected guess: day

    Example story paragraph:
    In the afternoon, as the village stirred with activity, Sarah joined her neighbors in the bustling marketplace.\
    Amidst stalls laden with fresh produce and the lively chatter of vendors and customers alike, she exchanged greetings and stories with familiar faces,\
    weaving the fabric of community that bound them together.
    
    Expected guess: day

    Example story paragraph:
    Under the velvet embrace of the starlit night sky, a mysterious tale unfolds in the shadowed corners of a forgotten town. \
    The moon, a solitary sentinel, casts its silvery glow upon the cobblestone streets, illuminating secrets hidden in the darkness.

    Expected guess: night

    Example story paragraph:
    As the sun dipped below the horizon, painting the sky with hues of crimson and gold, the sleepy town of Willowbrook stirred to life once more. \
    In the tranquil streets lined with quaint cottages and flickering lanterns, a tale of love and longing began to unfold.

    Expected guess: night

    Example story paragraph:
    Hey man! what's up.

    Expected guess: Since, we're not able to guess anything, then by default you should output day
    """

instruction = "Guess the background scene for the story paragraph:\n\n {text}"
template_time = Template(instruction, system_prompt)

## loading LLaMa-2-7B-chat-hf............................................................................

class LLM:

    def __init__(
        self,
        model_path = model_path,
        hf_aut = hf_aut,
        torch_dtype = torch.float16,
        top_k = 50,
        max_tokens = 3000,
        device_map = 'xpu',
        temperature = 0.1,
        optimize = True,
    ) -> None:
        
        self.device_map = device_map
        self.torch_dtype = torch_dtype
        self.hf_aut = hf_aut
        self.model_path = model_path
        self.generator = torch.Generator()
        self.pipeline = self._load_pipeline(model_path = model_path, 
                                            torch_dtype = torch_dtype, 
                                            hf_aut = hf_aut, 
                                            device_map = device_map, 
                                            top_k = top_k,
                                            max_tokens = max_tokens)

        self.llm = HuggingFacePipeline(pipeline = self.pipeline, model_kwargs = {'temperature': temperature})

    def _load_pipeline(
        self, model_path, torch_dtype, hf_aut, device_map, top_k, max_tokens
    ):
        tokenizer = AutoTokenizer.from_pretrained(model_path,
                                          token = hf_aut,)
        
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map = 'xpu',
            torch_dtype = torch_dtype,
            token = hf_aut,
            )
        
        pipe = transformers.pipeline(
            task = "text-generation",
            model = model,
            device_map = device_map,
            tokenizer = tokenizer,
            return_full_text = True,
            max_new_tokens = max_tokens,
            do_sample = True,
            top_k = top_k,
            num_return_sequences = 1,
            eos_token_id = tokenizer.eos_token_id
            )

        return pipe
        
        
    def clean_output(self, text):
        text = text['text']
        split = text.split(E_INST)
        if len(split) == 0: return " "
        elif len(split) == 1: return split[0]
        else:
            split = split[1:]
            cur = ""
            for i in split: cur += i
            return cur
            
    def generate(self, template, text):
        prompt = PromptTemplate(template = template, input_variables = ["text"])
        model = LLMChain(prompt = prompt, llm = self.llm)
        return self.clean_output(model.invoke(text))
    
    def check_time(self, text):
        if "day" in text: return 0
        return 1
    
    def check_scene(self, text):
        for key, value in scene.items():
            if key in text: return value
        return 3
    
    def get_base(self, text):
        output = self.generate(template_scene, text)
        output = output.lower()
        sc = self.check_scene(output)
        if sc == 13: return sc
        output = self.generate(template_time, text)
        return sc + self.check_time(output)

    def get_story(self, text):
        return self.generate(template_story, text)

    def get_prompt(self, text):
        return self.generate(template_prompt, text)

try:
    llama = LLM(model_path, hf_aut, top_k = 50, max_tokens = 3000, temperature = 0.1)
except:
    print("Difficulty loading LLM...\nCan't generate the story now")
    

## loading image generator................................................................................
    
class Img2ImgModel:

    def __init__(
        self,
        model_id_or_path: str,
        device: str = "xpu",
        torch_dtype: torch.dtype = torch.bfloat16,
        optimize: bool = True,
        warmup: bool = False,
        scheduler: bool = True,
    ) -> None:
        
        self.device = device
        self.data_type = torch_dtype
        self.scheduler = scheduler
        self.generator = torch.Generator()
        self.pipeline = self._load_pipeline(model_id_or_path, torch_dtype)

    def _load_pipeline(
        self, model_id_or_path: str, torch_dtype: torch.dtype
    ) -> StableDiffusionImg2ImgPipeline:
        
        model_path = Path(f"{model_dir}/{model_id_or_path}")
        
        if model_path.exists():
            load_path = model_path
        else:
            load_path = model_id_or_path
            
        pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            load_path,
            torch_dtype = torch_dtype,
            use_safetensors = True,
            variant = "fp16",
        )
        if self.scheduler:
            pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                pipeline.scheduler.config
            )
        if not model_path.exists():
            try:
                print(f"Attempting to save the model to {model_path}...")
                pipeline.save_pretrained(f"{model_path}")
                print("Model saved.")
            except Exception as e:
                print(f"An error occurred while saving the model: {e}. Proceeding without saving.")
        pipeline = pipeline.to(self.device)
        return pipeline

    def get_image(self, prompt) -> Image.Image:
        image_number = 3
        try:
            image_number = llama.get_base(prompt)
        except:
            image_number = 3
        if image_number < 1 or image_number > 13:
            image_number = 3
        img = Image.open(f'{base}/{image_number}'+'.jpg')
        img = img.resize((800, 500))
        return img

    def generate_images(
        self,
        prompt: str,
        num_inference_steps: int = 200,
        strength: float = 0.75,
        guidance_scale: float = 7.5,
        batch_size: int = 1,
    ):
        init_image = self.get_image(prompt)
        try:
            prompt = llama.get_prompt(prompt)
        except:
            prompt = prompt

        try:
            image = self.pipeline(
                prompt = prompt,
                image = init_image,
                strength = strength,
                guidance_scale = guidance_scale,
                num_inference_steps=num_inference_steps,
            ).images
        
            return image[0]

        except:
            return init_image

## streamlit application..................................................................................



st.set_page_config(page_title = "app",
				page_icon = '🤖',
                    layout = 'centered',
                    initial_sidebar_state = 'collapsed')

st.markdown("<h1 style='text-align: center;'>🤖 Image Story GenAI 🏡</h1>", unsafe_allow_html = True)
st.markdown("<h5 style='text-align: justify;'> \
		  This is a simple story generator. Just enter a brief description about your story below and and wait for some time. \
		  A creative story with image illustration will be generated.<br>This project is using Meta Llama-2-7B-chat-hf LLM from Hugging face \
		  for text generation and stable diffusion models (listed in the selectbox below) for image generation \
            </h1>", unsafe_allow_html = True)

st.write("")

label1 = 'Select the Diffusion Model'
sd_model = st.selectbox(
    label1,
     (model_ids[0],
     model_ids[1])
    )

st.write("")

label2 = "Story Description"
story_description = st.text_input(label2)
    

m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: rgb(30, 30, 120);
    width: 150px
}
</style>""", unsafe_allow_html=True)


col1, col2 = st.columns([3.4, 1])

with col1:
    submit_g = st.button('Generate Story')
with col2:
    submit_c = st.button('Clear Story')


def display_image(img, width = 600):
     st.image(img, width = width)

def display_text(text):
     st.write(
		f"<div style='text-align: justify;'>"
		f"{text}"
		"</div>",
		unsafe_allow_html=True
	)

model_cache = {}

if submit_g:
	display_text("Generating story for you...😊")
	story = llama.get_story(story_description)
	partial_stories = split_paragraphs(story)
	for i, parts in enumerate(partial_stories):
		model_key = (sd_model, "xpu")
		if model_key not in model_cache:
			model_cache[model_key] = Img2ImgModel(sd_model, device = "xpu")
		prompt = parts
		model = model_cache[model_key]
		if not prompt:
			prompt = "a village man" 
		display_text(prompt) 
		try:
			start_time = time.time()
			image = model.generate_images(prompt = prompt,)
			display_image(image)
		except:
			display_text("An Error Occurred...☠️")

if submit_c:
    st.write("Generate a new story")

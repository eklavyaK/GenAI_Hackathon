# Problem Statement

### Team leader Email : [Eklavya Kumar](eklavyakumarsingh100@gmail.com)
## Interactive story telling using Generative AI
Develop an innovative platform for interactive storytelling that employs AI-driven tools, allowing users to actively shape the plot and characters through their input using use of Intel®️ oneAPI as the primary programming paradigm.
The aim is to craft captivating visual narratives using advanced AI techniques such as Stable Diffusion or Gen AI models. 
The interactive storytelling experience is designed to immerse users in a personalized and distinctive narrative, facilitated by generative AI technology, fostering engagement and creativity.


## Intel OneAPI toolkit libraries used:
1. **Intel® oneAPI intel_extension_for_pytorch** : Optimizes PyTorch for Intel hardwares. It provides performance optimizations for a variety of PyTorch operations, including:
Operator optimizations, Graph optimizations &Runtime optimizations:
2. **Intel® oneAPI Math Kernel Library (oneMKL)**: Leverage oneMKL for optimized mathematical operations, improving the overall performance of machine learning algorithms and computations.

## Workflow 1:
![Workflow 1](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/images/workflow1.png)

In this workflow we used a text to image generator stable diffusion model. 
The steps of the overall workflow is as follows: 
1. User gives a prompt about the plot of the story and characters involved. 
2. A creative story is generated using LLM model (OpenAI model = 'gpt-3.5-turbo', using API Key) in about 1000-1500 words. 
3. The story is splitted into different paragraphs of around 150-200 words. 
4. Each paragraph is sent to the LLM model to generate a simple, straightforward and small size prompt defining the characters and surrounding \ scenario of that paragraph. 
   The LLM model is prompted to follow some rules inorder to generate this prompts so as to make it easier for stable diffusion model to generate images based on simple and small prompts describing the part of story in that paragraph 
5. **LLM generated prompt** is sent to the Stable diffusion model to generate image for each part of story seperately.

## Workflow 2:
![Workflow 2](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/images/workflow2.png)

In this workflow we used a image to image generator stable diffusion model. 
The steps of the overall workflow is as follows: 
1. User gives a prompt about the plot of the story and characters involved. 
2. A creative story is generated using LLM model (OpenAI model = 'gpt-3.5-turbo') in about 1000-1500 words. 
3. The story is splitted into different paragraphs of around 150-200 words.
4. Each paragraph is sent to the LLM model to generate a simple, straightforward and small size prompt defining the characters and surrounding\scenario of that paragraph. The LLM model is prompted to follow some rules inorder to generate this prompts so as to make it easier for stable diffusion model to generate images based on simple and small prompts describing the part of story in that paragraph.
5. Each paragraph is sent to the LLM model again to give a integer number back (between 1-13) the number returned is used to **retrieve a base image** out of the 13 base images already saved in a folder. Each base image represent a location/surrounding in either daytime or nighttime. The LLM model infere from the paragraph what is the most probable/suitable location and day/night time the events described in that paragraph corresponds and return the appropriate number which is then used to retrieve that base image. This base image responsible to affect the colors of the image generated for this paragraph.
6. **Retrieved Base image & generated prompt** is sent to the image to image Stable diffusion model to generate image for each part of story seperately.

## Workflow 3
OpenAI has limits on number of queries per minute. Most of times it stops giving responses throwing that quota is over which we didn't wanted to persist in our streamlit app.
Hence we decided to use a open source model. Meta's Llama-2-7B-chat-hf seemed to be best option depending on the availability of our resources. Since Llama2 model being as accurate as gpt-3.5-turbo. We changed the rules from prompt.In this workflow we used a image to image generator stable diffusion model. 
The steps of the overall workflow is as follows: 
1. User gives a prompt about the plot of the story and characters involved. 
2. A creative story is generated using Llama2 in about 1000-1500 words. 
3. The story is splitted into different paragraphs of around 150-200 words.
4. Each paragraph is sent to the LLM model to generate a simple, straightforward and small size prompt defining the characters and surrounding\scenario of that paragraph. The LLM model is prompted to follow some rules inorder to generate this prompts so as to make it easier for stable diffusion model to generate images based on simple and small prompts describing the part of story in that paragraph. 
5. Each paragraph is sent to the LLM model again to guess the background scene (city, village, sea, space, forest, room etc) of the scene depicted in the paragraph, by default we take scene as village. Further based the response we search for the scene in the output of the LLM. After we make another query from the LLM about when (day or night) the scene is taking place, by default we take time as day. Now by combining these two responses a base image for the current scene is selected.
6. **Retrieved Base image & generated prompt** is sent to the image to image Stable diffusion model to generate the final image illustration for each scene of the story seperately.

### Streamlit App
The app is yet to be deployed. It is difficult to find free cloud provider which could run the app due to it's high runtime space complexity. The models (Llama-2 and stable diffusion) combined take around 15 GB of memory. Link of the app will be updated here as soon as we deploy our work.

### Example of some base images used:
Base image corresponding to surrounding of a village at night<br>
![image 1](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/base/4.jpg)

Base image corresponding to surrounding of a forest in day<br>
![image 2](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/base/5.jpg)

## An example story generated using the above workflow:
**Prompt by the user** : A astrounaut travelling through space in his spacecraft <br>
![image 1](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/images/1.png)
![image 1](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/images/2.png)
![image 1](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/images/3.png)
![image 1](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/images/4.png)
![image 1](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/images/5.png)

## Future Scope:
Use of better LLMs and Image generators for accurate image generation. <br>
Optimization of code for easy deployment of the streamlit app. <br>
Better prompt engineering to exploit features of the models in better way.

## Video description:
[![Video](https://github.com/eklavyaK/GenAI_Hackathon/blob/master/images/Thumbnail.jpg)](https://www.youtube.com/watch?v=MAmnOYT1qhU)

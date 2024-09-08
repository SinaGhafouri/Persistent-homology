<h1>Topological data analysis</h1>

Topological data analysis (TDA) is a set of tools that describe the shape of data based on the presence of holes. Persistent homology (PH) is the main tool of TDA to calculate homology groups of topological spaces.

PH is beneficial for all kinds of data types like point clouds, digital images, networks, time series, etc., if we can assign a metric to them. The key point in computing the PH of a data set is to assign a parameter (which we call the proximity parameter) to the data and change it continuously while we count the number of topological holes in the data set and record it at that specific proximity parameter. This process is called filtration. For example, in a point cloud in 2D space, we can assign a 2D ball (circle) to each point and increase their radii (proximity parameter). Based on a certain method (like the Vietoris–Rips complex), we create a topological space (simplicial complex for point clouds). This simplicial complex has a certain number of topological holes in different dimensions, which we call Betti numbers ($\beta$). For example, $\beta_0$ is the number of components, $\beta_1$ is the number of 1D holes, $\beta_2$ is the number of 2D holes, and so on. Now we can represent this calculation with different diagrams with respect to the proximity parameter. As shown in this [notebook](Ripser%20-%20Simplicial%20Complex.ipynb) you can calculate the PH for point cloud datasets. Inspired by this great <a href="https://www.youtube.com/watch?v=h0bnG1Wavag&t">video</a>, I wrote [this python code](playground/custom_point_cloud.py) to give us an interactive playground for creating a point cloud dataset and calculating the persistent homology in real time while also representing it in some diagrams. Here is a video of the code running:

<a href="https://www.youtube.com/watch?v=iC-O_JGlpIQ">
    <img src="https://img.youtube.com/vi/iC-O_JGlpIQ/maxresdefault.jpg" alt="Watch the video" width="400"/>
</a>

These diagrams give us an understanding of the shape of the whole dataset, which we also call the study of the global characteristics of the dataset.

For a digital image, the procedure is a little different. Although here we have to find a proximity parameter and change it like the previous one while counting the holes. Since digital images have a cubical structure, one approach to mapping a digital image to topological space uses combinatorial structures called cubical complexes. As shown in this [notebook](Gudhi%20-%20Cubical%20Complex.ipynb) you can calculate the PH for digital image datasets. For a hands-on experience to grasp the concept of this filtration better, see [this notebook](playground/Cubical%20Complex%20-%20Filtration.ipynb). In this [directory](playground), you can find other notebooks and play with them. You can run these notebooks in Google Colab; please make sure to install the required packages first. 

<span style="color: green;"><b>For a detailed and comprehensive explanation of TDA cocepts and its applications, refer to this</span> <a href="https://epjdatascience.springeropen.com/articles/10.1140/epjds/s13688-017-0109-5">paper</a>.</b>





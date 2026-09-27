<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white)](https://json.org)
[![HackerRank](https://img.shields.io/badge/-HackerRank-2EC866?style=for-the-badge&logo=HackerRank&logoColor=white)](https://hackerrank.com)

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">HackerRank Orchestrate AI Agent Challenge</h3>

  <p align="center">
    A Python-based AI agent orchestration system built for the HackerRank Orchestrate coding challenge to process complex, multi-modal datasets and generate schema-validated JSON outputs.
    <br />
    <br />
    <strong>Tags:</strong> <code>python</code>, <code>ai-agents</code>, <code>hackerrank</code>, <code>orchestration</code>, <code>llm</code>, <code>data-processing</code>, <code>multi-modal</code>, <code>json-validation</code>, <code>automation</code>, <code>etl</code>, <code>backend</code>, <code>api-integration</code>, <code>scripting</code>, <code>dataset-parsing</code>, <code>error-handling</code>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This repository contains the solution for the HackerRank Orchestrate coding challenge. The system is designed to build and test AI agents capable of parsing unstructured and multi-modal data. It processes a complex provided dataset consisting of business accounts, daily notifications, group details, and media files (both audio and images) to extract, validate, and normalize information into a clean JSON structure. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

* Python 3.10+
* pip
  ```sh
  python -m pip install --upgrade pip
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/SeanRDC/hackerrank-orchestrate.git
   ```
2. Install necessary Python packages
   ```sh
   pip install google-genai pandas python-dotenv
   ```
3. Set up your environment variables for the required LLM providers.
    ```sh
    GEMINI_API_KEY="your_api_key_here"
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

To execute the main orchestration pipeline, run the primary Python script located in the `code` directory:

```sh
cd code
python main.py
```

The system will ingest the CSV records and media files from the `dataset` directory, process them through the configured AI agents defined in `AGENTS.md`, and output the validated results.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] Initialize project structure and dataset directories
- [x] Configure base AI agent behaviors (`AGENTS.md`)
- [x] Implement multi-modal parsing for audio/images
- [x] Integrate CSV ingestion (`business_accounts.csv`, `groups.csv`, etc.)
- [x] Build robust retry and schema-validation mechanisms in `main.py`
- [x] Finalize and test HackerRank Orchestrate submission

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- PROJECT STRUCTURE -->
## Project Structure

```text
hackerrank-orchestrate-SeanRDC/
├── .vscode/
├── code/
│   ├── README.md
│   └── main.py
├── dataset/
│   ├── media/
│   │   ├── audio/
│   │   │   └── (vn_001.mp3 to vn_015.mp3)
│   │   └── images/
│   │       └── (img_001.jpg to img_026.jpg)
│   ├── business_accounts.csv
│   ├── daily_notification_summary.csv
│   ├── group_members.csv
│   ├── groups.csv
│   ├── images.csv
│   ├── message_events.csv
│   ├── message_history.csv
│   ├── messages.csv
│   ├── output.csv
│   ├── sample_messages.csv
│   ├── user_business_history.csv
│   ├── users.csv
│   └── voice_notes.csv
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── problem_statement.md
└── test_gemini.py
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Sean Rhani Jarin Dela Cruz

Project Link: [https://github.com/SeanRDC/hackerrank-orchestrate](https://github.com/SeanRDC/hackerrank-orchestrate) <br />
LinkedIn Link: [https://www.linkedin.com/in/sean-rhani-dela-cruz-834573334/](https://www.linkedin.com/in/sean-rhani-dela-cruz-834573334/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

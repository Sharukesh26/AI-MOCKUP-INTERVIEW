using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.Networking;
using System.Text;
using TMPro;
using UnityEngine.Windows.Speech;

public class ARPrepZoneAI : MonoBehaviour
{
    public TMP_InputField candidateNameInput;
    public TMP_InputField companyNameInput;
    public TMP_InputField jobDescriptionInput;
    public TMP_InputField resumeTextInput;
    public TextMeshProUGUI matchResults;
    public TextMeshProUGUI questionText;
    public Button generateQuestionsButton;
    public Button nextQuestionButton;
    public Button recordAnswerButton;
    
    private List<string> interviewQuestions = new List<string>();
    private int currentQuestionIndex = 0;
    private DictationRecognizer dictationRecognizer;
    private string recordedAnswer = "";
    
    private string API_KEY = "YOUR_GEMINI_API_KEY";
    private string AI_API_URL = "https://api.google.com/gemini/generate";

    void Start()
    {
        generateQuestionsButton.onClick.AddListener(GenerateInterviewQuestions);
        nextQuestionButton.onClick.AddListener(NextQuestion);
        recordAnswerButton.onClick.AddListener(StartVoiceRecording);

        dictationRecognizer = new DictationRecognizer();
        dictationRecognizer.DictationResult += (text, confidence) =>
        {
            recordedAnswer = text;
            Debug.Log("Recognized: " + text);
        };
        dictationRecognizer.DictationComplete += (completionCause) =>
        {
            if (completionCause != DictationCompletionCause.Complete)
                Debug.LogError("Dictation stopped unexpectedly.");
        };
    }

    void GenerateInterviewQuestions()
    {
        string candidateName = candidateNameInput.text;
        string companyName = companyNameInput.text;
        string jobDesc = jobDescriptionInput.text;
        string resumeText = resumeTextInput.text;

        if (string.IsNullOrEmpty(candidateName) || string.IsNullOrEmpty(jobDesc) || string.IsNullOrEmpty(resumeText))
        {
            Debug.LogError("Please enter all required fields.");
            return;
        }

        string prompt = "Generate interview questions for a job description: " + jobDesc + " and resume: " + resumeText + " for " + candidateName + " at " + companyName;

        StartCoroutine(SendAIRequest(prompt));
    }

    IEnumerator SendAIRequest(string prompt)
    {
        var jsonData = JsonUtility.ToJson(new { prompt = prompt });
        var request = new UnityWebRequest(AI_API_URL, "POST")
        {
            uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(jsonData)),
            downloadHandler = new DownloadHandlerBuffer()
        };
        request.SetRequestHeader("Content-Type", "application/json");
        request.SetRequestHeader("Authorization", "Bearer " + API_KEY);

        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Error: " + request.error);
        }
        else
        {
            string response = request.downloadHandler.text;
            interviewQuestions = ParseResponse(response);
            currentQuestionIndex = 0;
            ShowQuestion();
        }
    }

    List<string> ParseResponse(string response)
    {
        List<string> questions = new List<string>();
        string[] lines = response.Split('\n');
        foreach (string line in lines)
        {
            if (!string.IsNullOrWhiteSpace(line))
                questions.Add(line.Trim());
        }
        return questions;
    }

    void ShowQuestion()
    {
        if (currentQuestionIndex < interviewQuestions.Count)
        {
            questionText.text = "Question: " + interviewQuestions[currentQuestionIndex];
        }
        else
        {
            questionText.text = "Interview Complete!";
        }
    }

    void NextQuestion()
    {
        if (currentQuestionIndex < interviewQuestions.Count - 1)
        {
            currentQuestionIndex++;
            ShowQuestion();
        }
    }

    void StartVoiceRecording()
    {
        dictationRecognizer.Start();
        Debug.Log("Voice recording started...");
    }
}
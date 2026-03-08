import QuestionInput from '../components/QuestionInput';

export default function Home() {
  const handleQuestionSubmit = (question) => {
    console.log('Question:', question);
    // Call API or handle question here
  };

  return (
    <div>
      <h1>Physics Explainer</h1>
      <QuestionInput onSubmit={handleQuestionSubmit} />
    </div>
  );
}

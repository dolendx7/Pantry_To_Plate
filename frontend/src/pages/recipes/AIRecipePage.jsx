import React, { useState, useEffect, useRef } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { useAuthStore } from '../../store/authStore';
import recipesService from '../../services/recipesService';
import pantryService from '../../services/pantryService';
import { 
  Sparkles, 
  MessageSquare, 
  Clock, 
  Flame, 
  ChefHat, 
  ChevronRight, 
  Plus, 
  X, 
  Send, 
  BookOpen, 
  Check, 
  ArrowRightLeft, 
  Loader2,
  UtensilsCrossed,
  Heart
} from 'lucide-react';
import useToastStore from '../../store/toastStore';

const CUISINES = ['Any', 'Indian', 'Italian', 'Chinese', 'Mexican', 'American', 'Continental'];

export default function AIRecipePage() {
  const { token } = useAuthStore();
  const toast = useToastStore.getState();
  const chatEndRef = useRef(null);

  const [activeTab, setActiveTab] = useState('generate'); // 'generate' | 'chat'
  const [pantryItems, setPantryItems] = useState([]);
  const [loadingPantry, setLoadingPantry] = useState(false);

  // Magic Generator Form State
  const [dietType, setDietType] = useState('veg'); // 'veg' | 'non-veg' | ''
  const [cuisine, setCuisine] = useState('Any');
  const [maxTime, setMaxTime] = useState('');
  const [maxCalories, setMaxCalories] = useState('');
  const [manualIngredients, setManualIngredients] = useState([]);
  const [ingredientInput, setIngredientInput] = useState('');
  const [generating, setGenerating] = useState(false);
  const [recipes, setRecipes] = useState([]);

  // Chatbot State
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: "Namaste! I am your AI Pantry Chef. Ask me anything, or let me suggest recipes based on your active pantry ingredients!",
      recipes: []
    }
  ]);

  // Modal State for viewing recipe details
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [savingRecipeId, setSavingRecipeId] = useState(null);

  // Fetch pantry items to show as quick reference or use in prompt
  const fetchPantry = async () => {
    try {
      setLoadingPantry(true);
      const data = await pantryService.getItems(token);
      setPantryItems(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPantry(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchPantry();
    }
  }, [token]);

  // Scroll to bottom of chat when messages update
  useEffect(() => {
    if (activeTab === 'chat' && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, activeTab]);

  // Handle adding manual ingredient chips
  const handleAddIngredient = (e) => {
    e.preventDefault();
    const val = ingredientInput.trim();
    if (!val) return;
    if (!manualIngredients.includes(val)) {
      setManualIngredients([...manualIngredients, val]);
    }
    setIngredientInput('');
  };

  const handleRemoveIngredient = (ing) => {
    setManualIngredients(manualIngredients.filter(i => i !== ing));
  };

  // Trigger Magic Recipe Generation
  const handleGenerate = async (e) => {
    e.preventDefault();
    try {
      setGenerating(true);
      const payload = {
        diet_type: dietType,
        cuisine: cuisine === 'Any' ? '' : cuisine,
        ingredients: manualIngredients,
        max_time: maxTime ? parseInt(maxTime) : null,
        calories: maxCalories ? parseInt(maxCalories) : null
      };
      const data = await recipesService.generateAiRecipes(token, payload);
      setRecipes(data);
      if (data.length === 0) {
        toast.error('No matching recipes found. Try adding more ingredients or widening filters!');
      } else {
        toast.success(`Generated ${data.length} delicious recipe suggestions!`);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  // Send message to AI Chef Chatbot
  const handleSendMessage = async (textToSend) => {
    const text = textToSend || chatInput.trim();
    if (!text) return;

    if (!textToSend) setChatInput('');

    // Add user message
    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      text
    };
    setMessages(prev => [...prev, userMsg]);
    setChatLoading(true);

    try {
      const data = await recipesService.chatWithAiChef(token, text);
      const botMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: data.message || data.error || 'Sorry, I could not process that.',
        recipes: data.recipes || []
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      const errText = err?.response?.data?.error || err?.message || 'AI Chef is temporarily unavailable. Please try again shortly.';
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: `⚠️ ${errText}`,
        recipes: []
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Save Recipe to Chef Recipe Book
  const handleSaveRecipe = async (recipe) => {
    try {
      setSavingRecipeId(recipe.recipe_id);
      await recipesService.addRecipe(token, {
        title: recipe.title,
        diet_type: recipe.diet_type || 'veg',
        prep_time: recipe.prep_time || 15,
        cook_time: recipe.cook_time || 15,
        servings: 4,
        difficulty: recipe.difficulty || 'easy',
        ingredients: recipe.matched_ingredients ? [...recipe.matched_ingredients, ...recipe.missing_ingredients] : [],
        steps: recipe.steps || [`Prep all ingredients.`, `Combine ingredients and heat to simmer.`, `Serve hot.`],
        cuisine: recipe.cuisine || 'Universal',
        calories: recipe.calories || 300,
        protein: recipe.protein || 8,
        carbs: recipe.carbs || 30,
        fat: recipe.fat || 10
      });
      // Update local state to mark as saved or show toast
      toast.success(`"${recipe.title}" added to your Recipe Book!`);
    } catch (err) {
      console.error(err);
    } finally {
      setSavingRecipeId(null);
    }
  };

  const quickChats = [
    "What can I cook with my current pantry?",
    "Suggest a quick 15-minute dinner recipe",
    "I have extra veggies. What should I prepare?",
  ];

  return (
    <DashboardLayout title="AI Recipe Generator" subtitle="Generate real-time chef recommendations and pantry matching">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Magic Canvas Title Board */}
        <div className="clean-card-dark rounded-3xl p-6 md:p-8 mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
          <div className="absolute inset-0 stripes-pattern opacity-5 pointer-events-none" />
          <div className="flex items-center gap-4 relative z-10">
            <div className="p-4 bg-white/10 rounded-2xl">
              <ChefHat className="w-10 h-10 text-white animate-bounce" />
            </div>
            <div>
              <h2 className="text-xl md:text-2xl font-extrabold tracking-tight text-white">Virtual Chef AI Studio</h2>
              <p className="text-stone-300 text-xs md:text-sm mt-1 font-medium">Create recipe wonders matching your kitchen stock</p>
            </div>
          </div>
          
          <div className="flex gap-2.5 shrink-0 relative z-10">
            <button
              onClick={() => setActiveTab('generate')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-sm flex items-center gap-1.5 cursor-pointer ${activeTab === 'generate' ? 'bg-white text-orange-600' : 'bg-white/10 hover:bg-white/20 text-white'}`}
            >
              <Sparkles className="w-4.5 h-4.5" /> Magic Generator
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-sm flex items-center gap-1.5 cursor-pointer ${activeTab === 'chat' ? 'bg-white text-orange-600' : 'bg-white/10 hover:bg-white/20 text-white'}`}
            >
              <MessageSquare className="w-4.5 h-4.5" /> Chat with Chef
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* LEFT SECTION (Tab Content) */}
          <div className="lg:col-span-8 space-y-8">
            
            {activeTab === 'generate' ? (
              /* TAB 1: MAGIC GENERATOR */
              <div className="space-y-8">
                
                {/* Custom Configuration Form */}
                <div className="clean-card-base rounded-2xl p-6">
                  <h3 className="text-sm font-bold text-slate-800 flex items-center gap-1.5 border-b border-slate-200/60 pb-3 mb-5">
                    <Sparkles className="w-4.5 h-4.5 text-orange-500" /> Filter & Match Settings
                  </h3>

                  <form onSubmit={handleGenerate} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      
                      {/* Diet Selection */}
                      <div>
                        <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">Diet Preference</label>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => setDietType('veg')}
                            className={`flex-1 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${dietType === 'veg' ? 'bg-emerald-50 border-emerald-300 text-emerald-700 shadow-sm' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'}`}
                          >
                            Vegetarian
                          </button>
                          <button
                            type="button"
                            onClick={() => setDietType('non-veg')}
                            className={`flex-1 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${dietType === 'non-veg' ? 'bg-red-50 border-red-300 text-red-700 shadow-sm' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'}`}
                          >
                            Non-Veg
                          </button>
                        </div>
                      </div>

                      {/* Cuisine Selector */}
                      <div>
                        <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">Cuisine Theme</label>
                        <select
                          value={cuisine}
                          onChange={(e) => setCuisine(e.target.value)}
                          className="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs text-slate-800 outline-none focus:border-orange-500 bg-white"
                        >
                          {CUISINES.map(c => (
                            <option key={c} value={c}>{c}</option>
                          ))}
                        </select>
                      </div>

                      {/* Cook Time Slider */}
                      <div>
                        <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">Max Time (Minutes)</label>
                        <input 
                          type="number" 
                          placeholder="e.g. 30"
                          value={maxTime}
                          onChange={(e) => setMaxTime(e.target.value)}
                          className="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs text-slate-800 outline-none focus:border-orange-500 placeholder-slate-400"
                        />
                      </div>

                    </div>

                    {/* Manual Ingredients Box */}
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">
                        Add Extra Ingredients (Optional)
                      </label>
                      <div className="flex gap-2">
                        <input 
                          type="text" 
                          placeholder="Add ingredients not in your pantry (e.g. Mushroom, Basil)"
                          value={ingredientInput}
                          onChange={(e) => setIngredientInput(e.target.value)}
                          className="flex-1 px-3.5 py-2 border border-slate-200 rounded-xl text-xs text-slate-800 outline-none focus:border-orange-500 placeholder-slate-400"
                        />
                        <button
                          type="button"
                          onClick={handleAddIngredient}
                          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center gap-1"
                        >
                          <Plus className="w-4 h-4" /> Add
                        </button>
                      </div>

                      {manualIngredients.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {manualIngredients.map(ing => (
                            <span 
                              key={ing}
                              className="px-2.5 py-1 bg-orange-50/60 border border-orange-100 text-orange-700 rounded-full text-[10px] font-bold flex items-center gap-1"
                            >
                              {ing}
                              <X 
                                className="w-3 h-3 cursor-pointer hover:text-orange-950" 
                                onClick={() => handleRemoveIngredient(ing)}
                              />
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <button 
                      type="submit"
                      disabled={generating}
                      className="w-full py-3 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-xl text-sm font-bold shadow-sm hover:shadow transition-all cursor-pointer flex items-center justify-center gap-2"
                    >
                      {generating ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" /> Concocting Chef Recipes...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4.5 h-4.5 text-white" /> Generate Chef Recommendations
                        </>
                      )}
                    </button>

                  </form>
                </div>

                {/* Recommendations List */}
                <div>
                  <h3 className="text-base font-bold text-slate-800 border-b border-slate-200/60 pb-3.5 mb-5">
                    Chef Recommendations
                  </h3>

                  {recipes.length === 0 ? (
                    <div className="premium-card-orange rounded-2xl p-12 text-center">
                      <div className="w-12 h-12 bg-orange-50 text-orange-500 rounded-full flex items-center justify-center mx-auto mb-3">
                        <UtensilsCrossed className="w-6 h-6" />
                      </div>
                      <h4 className="text-sm font-bold text-slate-800">No suggestions compiled yet</h4>
                      <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto leading-relaxed">
                        Tap "Generate Chef Recommendations" above to search recipes matching your active pantry ingredients.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {recipes.map((r, idx) => (
                        <div 
                          key={r.recipe_id || idx}
                          className={`${r.diet_type === 'non-veg' ? 'premium-card-red' : 'premium-card-green'} rounded-2xl p-5 flex flex-col justify-between`}
                        >
                          <div>
                            {/* Card Header: Score badge */}
                            <div className="flex justify-between items-start mb-3">
                              <span className={`text-[9px] font-extrabold uppercase px-2 py-0.5 rounded-full ${r.diet_type === 'non-veg' ? 'bg-red-50 text-red-650 border border-red-100' : 'bg-emerald-50 text-emerald-700 border border-emerald-100'}`}>
                                {r.diet_type === 'non-veg' ? 'Non-Veg' : 'Veg'}
                              </span>
                              <span className="text-[10px] bg-orange-50 text-orange-600 font-extrabold px-2.5 py-0.5 rounded-full">
                                {r.match_score}% Match
                              </span>
                            </div>

                            <h4 className="text-base font-bold text-slate-800 leading-snug">{r.title}</h4>
                            <p className="text-[11px] text-slate-400 uppercase tracking-wide font-extrabold mt-0.5">{r.cuisine || 'Universal'} • {r.difficulty || 'Easy'}</p>

                            {/* Clock and calories */}
                            <div className="flex items-center gap-4 mt-3 text-xs text-slate-500 font-semibold">
                              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {r.total_time || 20} mins</span>
                              <span className="flex items-center gap-1"><Flame className="w-3.5 h-3.5 text-amber-500" /> {r.calories || 350} kcal</span>
                            </div>

                            {/* Match Progress slider */}
                            <div className="w-full bg-slate-100 h-1 rounded-full overflow-hidden mt-3.5 mb-4">
                              <div className="h-full bg-orange-500 rounded-full" style={{ width: `${r.match_score}%` }} />
                            </div>

                            {/* Ingredients overview */}
                            <div className="space-y-1 mt-3">
                              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Pantry matching</p>
                              {r.matched_ingredients && (
                                <p className="text-xs text-slate-600 truncate">
                                  <span className="text-emerald-500 font-bold">✓</span> {r.matched_ingredients.join(', ')}
                                </p>
                              )}
                              {r.missing_ingredients && r.missing_ingredients.length > 0 && (
                                <p className="text-xs text-slate-600 truncate">
                                  <span className="text-red-400 font-bold">−</span> Missing: {r.missing_ingredients.join(', ')}
                                </p>
                              )}
                            </div>
                          </div>

                          <div className="flex gap-2.5 mt-6 border-t border-slate-100 pt-4">
                            <button
                              onClick={() => {
                                // Provide default steps if missing
                                const finalRecipe = {
                                  ...r,
                                  steps: r.steps || [
                                    "Prepare all vegetables and spices.",
                                    "Heat oil in a pan, add aromatic spices and saute.",
                                    "Add primary ingredients and cook thoroughly.",
                                    "Season with salt and pepper, garnish and serve hot."
                                  ]
                                };
                                setSelectedRecipe(finalRecipe);
                              }}
                              className="flex-1 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200/50 rounded-xl text-xs font-bold text-slate-700 flex items-center justify-center gap-1 transition-colors cursor-pointer"
                            >
                              <BookOpen className="w-3.5 h-3.5" /> Cooking Steps
                            </button>
                            <button
                              onClick={() => handleSaveRecipe(r)}
                              disabled={savingRecipeId === r.recipe_id}
                              className="px-3 py-2 bg-orange-50 hover:bg-orange-100 text-orange-600 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center justify-center"
                              title="Save to Recipe Book"
                            >
                              {savingRecipeId === r.recipe_id ? (
                                <Loader2 className="w-4 h-4 animate-spin text-orange-500" />
                              ) : (
                                <Heart className="w-4 h-4 fill-orange-50" />
                              )}
                            </button>
                          </div>

                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </div>
            ) : (
              /* TAB 2: AI PANTRY CHEF CHATBOT */
              <div className="clean-card-green-inner rounded-3xl p-5 h-[70vh] flex flex-col justify-between">
                
                {/* Chat Message Window */}
                <div className="flex-1 overflow-y-auto space-y-4 pr-2 mb-4 scrollbar-thin">
                  {messages.map(msg => (
                    <div 
                      key={msg.id}
                      className={`flex gap-3 max-w-[85%] ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
                    >
                      {/* Avatar */}
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm ${msg.sender === 'user' ? 'bg-orange-500 text-white' : 'bg-amber-100 border border-amber-200 text-amber-700 font-bold'}`}>
                        {msg.sender === 'user' ? 'U' : <ChefHat className="w-4.5 h-4.5" />}
                      </div>

                      {/* Text Bubble */}
                      <div className="space-y-3">
                        <div className={`p-4.5 rounded-2xl text-xs leading-relaxed shadow-sm ${msg.sender === 'user' ? 'bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-tr-none' : 'bg-slate-50 border border-slate-250/20 text-slate-800 rounded-tl-none font-medium'}`}>
                          {msg.sender === 'bot' ? (
                            <span style={{whiteSpace: 'pre-wrap'}}>
                              {msg.text.split(/(\*\*[^*]+\*\*)/).map((part, i) =>
                                part.startsWith('**') && part.endsWith('**')
                                  ? <strong key={i}>{part.slice(2, -2)}</strong>
                                  : <span key={i}>{part}</span>
                              )}
                            </span>
                          ) : msg.text}
                        </div>

                        {/* Inline recipe matches if bot suggested any */}
                        {msg.recipes && msg.recipes.length > 0 && (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
                            {msg.recipes.map((r, ri) => (
                              <div 
                                key={r.recipe_id || ri}
                                className="bg-white border border-slate-100 rounded-xl p-3.5 shadow-sm hover:shadow hover:-translate-y-0.5 transition-all flex flex-col justify-between"
                              >
                                <div>
                                  <div className="flex justify-between items-center mb-2">
                                    <h4 className="text-xs font-bold text-slate-800 truncate max-w-[120px]">{r.title}</h4>
                                    <span className="text-[9px] bg-orange-50 text-orange-600 font-bold px-1.5 py-0.5 rounded">
                                      {r.match_score}% match
                                    </span>
                                  </div>
                                  <p className="text-[10px] text-slate-400 font-medium">Cook: {r.cook_time || 20}m</p>
                                </div>
                                <button
                                  onClick={() => {
                                    // Make matching structure for modal
                                    const modalData = {
                                      ...r,
                                      matched_ingredients: r.matched || [],
                                      missing_ingredients: r.missing || [],
                                      steps: r.steps || [
                                        "Follow the standard preparation steps.",
                                        "Saute the ingredients in a hot cooking pan.",
                                        "Plate beautifully and enjoy!"
                                      ]
                                    };
                                    setSelectedRecipe(modalData);
                                  }}
                                  className="mt-3 py-1 bg-slate-50 hover:bg-slate-100 border border-slate-200/50 rounded-lg text-[10px] font-bold text-slate-700 flex items-center justify-center gap-1 cursor-pointer transition-colors"
                                >
                                  View Recipe <ChevronRight className="w-3 h-3" />
                                </button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                    </div>
                  ))}

                  {chatLoading && (
                    <div className="flex gap-3 max-w-[80%]">
                      <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
                        <ChefHat className="w-4.5 h-4.5 text-amber-700" />
                      </div>
                      <div className="bg-slate-50 border border-slate-100 rounded-2xl rounded-tl-none p-4 shadow-sm flex items-center gap-2">
                        <Loader2 className="w-4.5 h-4.5 animate-spin text-orange-500" />
                        <span className="text-xs text-slate-500 font-bold">Chef is thinking...</span>
                      </div>
                    </div>
                  )}
                  
                  <div ref={chatEndRef} />
                </div>

                {/* Pre-set suggested prompts */}
                {messages.length <= 1 && (
                  <div className="flex flex-wrap gap-2.5 mb-4 justify-center border-t border-slate-100 pt-4">
                    {quickChats.map(qc => (
                      <button
                        key={qc}
                        onClick={() => handleSendMessage(qc)}
                        className="px-3.5 py-1.5 bg-slate-50 hover:bg-orange-50 hover:text-orange-700 border border-slate-200/50 text-slate-600 rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-sm"
                      >
                        {qc}
                      </button>
                    ))}
                  </div>
                )}

                {/* Chat Input Console */}
                <div className="flex gap-2 border-t border-slate-100 pt-4 mt-auto">
                  <input 
                    type="text"
                    placeholder="Ask chef about recipes, pantry substitutions, or cooking guides..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-xs text-slate-800 outline-none focus:border-orange-500 transition-all placeholder-slate-400 bg-slate-50"
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    className="p-3 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-xl shadow-sm hover:shadow cursor-pointer transition-all flex items-center justify-center"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>

              </div>
            )}

          </div>

          {/* RIGHT SECTION: Quick Pantry Shelf list */}
          <div className="lg:col-span-4">
            <div className="clean-card-dark rounded-3xl p-5 shadow-sm">
              <h3 className="text-sm font-bold text-white border-b border-white/10 pb-3 mb-4 flex items-center gap-1.5">
                <BookOpen className="w-4.5 h-4.5 text-emerald-300" /> Active Pantry Stock
              </h3>

              <p className="text-[11px] text-stone-400 font-semibold mb-4 leading-relaxed">
                Here are the ingredients currently recorded in your pantry space. The AI Chef draws from these items automatically!
              </p>

              {loadingPantry ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-orange-500" />
                </div>
              ) : pantryItems.length === 0 ? (
                <div className="py-6 text-center text-slate-400 text-xs font-bold">
                  Pantry is currently empty.
                </div>
              ) : (
                <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-1 scrollbar-thin">
                  {pantryItems.map(item => (
                    <div 
                      key={item.id}
                      className="flex items-center justify-between p-2.5 rounded-xl bg-white/10 border border-white/10 text-xs font-semibold"
                    >
                      <span className="text-stone-300">{item.name}</span>
                      <span className="px-2 py-0.5 bg-orange-50 text-orange-600 rounded-lg text-[10px] font-bold">
                        {item.quantity} {item.unit}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

        </div>

      </div>

      {/* DETAILED RECIPE DETAILS MODAL */}
      {selectedRecipe && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-2xl w-full shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-orange-500 to-amber-500 p-5 md:p-6 text-white flex justify-between items-start relative">
              <div>
                <span className="text-[9px] bg-white/20 text-white font-extrabold uppercase px-2 py-0.5 rounded-full border border-white/10">
                  {selectedRecipe.cuisine || 'Universal'} • {selectedRecipe.difficulty || 'Easy'}
                </span>
                <h3 className="text-lg md:text-xl font-extrabold tracking-tight mt-1">{selectedRecipe.title}</h3>
                
                <div className="flex items-center gap-4 mt-3 text-xs text-white/90 font-medium">
                  <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Prep + Cook: {selectedRecipe.total_time || 20}m</span>
                  {selectedRecipe.calories && (
                    <span className="flex items-center gap-1"><Flame className="w-3.5 h-3.5 text-amber-300" /> {selectedRecipe.calories} kcal</span>
                  )}
                </div>
              </div>
              <button 
                onClick={() => setSelectedRecipe(null)}
                className="p-1.5 bg-white/10 hover:bg-white/20 text-white rounded-full transition-all cursor-pointer"
              >
                <X className="w-4.5 h-4.5" />
              </button>
            </div>

            {/* Modal Body Scroll Container */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              
              {/* Nutrition Gauges */}
              {(selectedRecipe.protein || selectedRecipe.carbs || selectedRecipe.fat) && (
                <div className="grid grid-cols-3 gap-4 border-b border-slate-100 pb-5">
                  <div className="bg-slate-50 rounded-xl p-3 text-center border border-slate-100">
                    <p className="text-[10px] text-slate-450 font-extrabold uppercase tracking-wide">Protein</p>
                    <p className="text-sm font-extrabold text-slate-800 mt-1">{selectedRecipe.protein || 8}g</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-3 text-center border border-slate-100">
                    <p className="text-[10px] text-slate-450 font-extrabold uppercase tracking-wide">Carbohydrates</p>
                    <p className="text-sm font-extrabold text-slate-800 mt-1">{selectedRecipe.carbs || 30}g</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-3 text-center border border-slate-100">
                    <p className="text-[10px] text-slate-450 font-extrabold uppercase tracking-wide">Fat</p>
                    <p className="text-sm font-extrabold text-slate-800 mt-1">{selectedRecipe.fat || 10}g</p>
                  </div>
                </div>
              )}

              {/* Ingredients Details */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Ingredients Checklist</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {/* Matched */}
                  {selectedRecipe.matched_ingredients && selectedRecipe.matched_ingredients.map(ing => (
                    <div key={ing} className="flex items-center gap-2 p-2 bg-emerald-50/50 border border-emerald-100 text-xs font-bold text-emerald-800 rounded-lg">
                      <Check className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                      <span>{ing}</span>
                    </div>
                  ))}
                  {/* Missing */}
                  {selectedRecipe.missing_ingredients && selectedRecipe.missing_ingredients.map(ing => (
                    <div key={ing} className="flex items-center gap-2 p-2 bg-red-50/50 border border-red-100 text-xs font-bold text-red-800 rounded-lg">
                      <span className="text-red-500 font-extrabold shrink-0">−</span>
                      <span>{ing} (missing)</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Ingredient Substitution suggestions */}
              {selectedRecipe.substitutions && selectedRecipe.substitutions.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Chef Substitution Tips</h4>
                  <div className="space-y-2">
                    {selectedRecipe.substitutions.map((sub, si) => (
                      <div key={si} className="flex items-start gap-2.5 p-3 bg-indigo-50/50 border border-indigo-100 text-xs font-bold text-indigo-850 rounded-xl">
                        <ArrowRightLeft className="w-4 h-4 text-indigo-500 mt-0.5 shrink-0" />
                        <div>
                          <span className="text-indigo-800 font-extrabold">{sub.ingredient}:</span>
                          <span className="text-slate-600 font-semibold ml-1.5">Replace with {sub.suggestions.join(' or ')}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Preparation Steps list */}
              <div className="space-y-3 border-t border-slate-100 pt-5">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Cooking Instructions</h4>
                <ol className="space-y-3.5">
                  {selectedRecipe.steps && selectedRecipe.steps.map((step, si) => (
                    <li key={si} className="flex gap-3 text-xs font-semibold text-slate-700 leading-relaxed">
                      <span className="w-5 h-5 rounded-full bg-orange-100 text-orange-700 font-extrabold flex items-center justify-center shrink-0 text-[10px]">
                        {si + 1}
                      </span>
                      <p className="mt-0.5">{step}</p>
                    </li>
                  ))}
                </ol>
              </div>

            </div>

            {/* Modal Footer */}
            <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex justify-end gap-2.5">
              <button
                onClick={() => setSelectedRecipe(null)}
                className="px-4 py-2 border border-slate-200 text-slate-600 rounded-xl text-xs font-bold hover:bg-slate-100 transition-colors cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleSaveRecipe(selectedRecipe);
                  setSelectedRecipe(null);
                }}
                className="px-4 py-2 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer flex items-center gap-1.5"
              >
                <Heart className="w-3.5 h-3.5 text-white fill-orange-500" /> Save Recipe
              </button>
            </div>

          </div>
        </div>
      )}

    </DashboardLayout>
  );
}

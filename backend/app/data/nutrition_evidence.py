"""
Pre-curated Authoritative Nutrition Evidence Dataset
Drawn from ICMR-NIN, WHO, ISSN, USDA, and Harvard School of Public Health.
Used by the RAG subsystem to answer evidence-based nutrition queries with citations.
"""

from typing import List, Dict, Any

EVIDENCE_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "title": "Protein Requirements for Health and Muscle Protein Synthesis",
        "source_name": "International Society of Sports Nutrition (ISSN) & ICMR-NIN",
        "author": "Jäger, R., Kerksick, C. M., et al. / ICMR-NIN Expert Committee",
        "category": "protein",
        "published_year": 2023,
        "url": "https://doi.org/10.1186/s12970-017-0177-8",
        "content": """
Protein is an essential macronutrient comprised of 20 amino acids (9 essential, which cannot be synthesized endogenously). 
For the general sedentary population, the standard Recommended Dietary Allowance (RDA) is 0.8 to 1.0 grams per kilogram of body weight per day (ICMR-NIN 2024 guidelines recommend ~0.83 g/kg for Indian adults).
For exercising individuals and athletes seeking to optimize muscle protein synthesis (MPS) and lean mass retention, the ISSN recommends a daily protein intake between 1.4 and 2.0 g/kg/day, with upper ranges of 1.6 to 2.4 g/kg/day during caloric deficits to prevent muscle catabolism.
High-quality complete protein sources containing all 9 essential amino acids include eggs, dairy (milk, paneer, curd, whey), poultry, fish, and soy (tofu, edamame, soy chunks). 
Plant-based diets can easily achieve complete amino acid profiles by pairing complementary grains and legumes (such as rice with dal or roti with rajma), providing sufficient leucine (~2.5-3g per meal) to trigger the mTOR pathway for MPS.
Protein provides 4 kilocalories per gram and possesses the highest Thermic Effect of Food (TEF) at ~20-30%, contributing to enhanced satiety and metabolic rate.
"""
    },
    {
        "title": "Dietary Fiber: Physiology, Gut Microbiome, and Metabolic Health",
        "source_name": "World Health Organization (WHO) & USDA Dietary Guidelines",
        "author": "Reynolds, A., Mann, J., et al. (WHO Systematic Review)",
        "category": "fiber",
        "published_year": 2022,
        "url": "https://doi.org/10.1016/S0140-6736(18)31809-9",
        "content": """
Dietary fiber comprises non-digestible carbohydrates and lignin naturally present in plants. It is broadly categorized into soluble and insoluble fiber.
Soluble fiber (found in oats, barley, beans, lentils, psyllium husk, apples, and citrus) dissolves in water to form a viscous gel that slows gastric emptying, blunts postprandial glucose spikes, and binds bile acids, significantly lowering LDL cholesterol.
Insoluble fiber (found in whole wheat flour, wheat bran, brown rice, nuts, cauliflower, and potato skins) adds fecal bulk, stimulates peristalsis, prevents constipation, and accelerates intestinal transit time.
The human colonic microbiome ferments prebiotic soluble fibers into Short-Chain Fatty Acids (SCFAs) such as acetate, propionate, and butyrate, which nourish colonocytes, reduce systemic inflammation, and enhance insulin sensitivity.
The recommended daily fiber intake is at least 14 grams per 1,000 kcal consumed, equating to 25 to 35 grams per day for healthy adults. Inadequate fiber intake is associated with higher risks of cardiovascular disease, colorectal cancer, type 2 diabetes, and obesity.
"""
    },
    {
        "title": "Dietary Sources and Bioavailability of Iron (Heme vs Non-Heme)",
        "source_name": "Harvard T.H. Chan School of Public Health & ICMR-NIN",
        "author": "Department of Nutrition, Harvard School of Public Health",
        "category": "micronutrients",
        "published_year": 2024,
        "url": "https://www.hsph.harvard.edu/nutritionsource/iron/",
        "content": """
Iron is an indispensable trace mineral required for hemoglobin synthesis in erythrocytes (transporting oxygen to tissues) and myoglobin in muscle fibers, as well as cellular energy production via electron transport chains.
Dietary iron exists in two chemical forms:
1. Heme iron: Found exclusively in animal flesh (poultry, red meat, seafood). It is absorbed at a relatively high and steady rate of 15% to 35%, unaffected by most dietary inhibitors.
2. Non-heme iron: Found in plant foods, dairy, eggs, and iron-fortified grains. Major vegetarian sources include lentils, chickpeas, kidney beans (rajma), soy chunks, spinach, methi (fenugreek leaves), pumpkin seeds, and poha (flattened rice).
Non-heme iron has lower baseline bioavailability (2% to 15%) because its absorption is inhibited by phytates in whole grains and polyphenols/tannins in tea and coffee.
Crucially, co-ingesting Vitamin C (ascorbic acid, found in lemon juice, amla, oranges, tomatoes) reduces ferric (Fe3+) iron to ferrous (Fe2+) iron, increasing non-heme absorption by up to 300%. Soaking, sprouting, and fermenting legumes also reduces phytate content.
"""
    },
    {
        "title": "Calcium and Vitamin D for Skeletal and Musculoskeletal Homeostasis",
        "source_name": "World Health Organization (WHO) & ICMR-NIN",
        "author": "FAO/WHO Joint Expert Consultation",
        "category": "micronutrients",
        "published_year": 2023,
        "url": "https://www.who.int/publications/i/item/9241546123",
        "content": """
Calcium is the most abundant mineral in the human body, with 99% sequestered in bones and teeth to provide structural rigidity. The remaining 1% circulates in blood and intracellular fluid, mediating neuromuscular contractions, vasodilation, blood clotting, and cell signaling.
The Recommended Dietary Allowance (RDA) for adults is 1,000 mg per day for men and women (increasing to 1,200 mg for women over 50 and adults over 70).
Rich dietary sources of calcium include:
- Dairy: Cow milk (300 mg per 250ml glass), paneer (480 mg per 100g), curd/yogurt (180 mg per cup).
- Plant-based: Calcium-set firm tofu (350 mg per 100g), ragi/finger millet (344 mg per 100g), white sesame seeds (til, 975 mg per 100g raw), amaranth, and dark leafy greens.
Adequate Vitamin D (calciferol, 600-800 IU daily) is mandatory for active intestinal calcium transport; without Vitamin D, only 10-15% of dietary calcium is absorbed compared to 30-40% with optimal 25-hydroxyvitamin D levels.
"""
    },
    {
        "title": "Hydration Physiology and Daily Water Requirements",
        "source_name": "European Food Safety Authority (EFSA) & National Academies of Medicine",
        "author": "EFSA Panel on Dietetic Products, Nutrition and Allergies",
        "category": "hydration",
        "published_year": 2022,
        "url": "https://doi.org/10.2903/j.efsa.2010.1459",
        "content": """
Water represents approximately 55% to 65% of adult human body mass, serving as the solvent for metabolic biochemical reactions, lubricating joints, facilitating thermoregulation via perspiration, and removing cellular waste through renal filtration.
Standard physiological fluid intake baselines are:
- ~2.5 to 3.0 liters per day for sedentary men.
- ~2.0 to 2.5 liters per day for sedentary women.
Baseline requirements can be estimated as 30 to 35 ml per kilogram of body weight, with supplemental fluid required during warm climates or vigorous exercise (~400 to 800 ml per hour of active sweating).
Mild dehydration (as little as 1% to 2% body weight loss from water) impairs cognitive function, alertness, subjective fatigue, and endurance exercise performance.
Beverages such as plain water, herbal tea, clear broths, and buttermilk (chaas) contribute directly to hydration. Fruits and vegetables like cucumbers, watermelon, and tomatoes also provide significant fluid content (~90-95% water by weight).
"""
    },
    {
        "title": "Energy Balance, Caloric Deficits, and Metabolic Adaptation",
        "source_name": "National Institutes of Health (NIH) & Cochrane Systematic Reviews",
        "author": "Hall, K. D., et al. (NIH Mathematical Modeling of Human Metabolism)",
        "category": "energy_balance",
        "published_year": 2023,
        "url": "https://doi.org/10.1016/S2213-8587(16)00081-4",
        "content": """
The first law of thermodynamics dictates that changes in human energy stores (fat, muscle, glycogen) equal energy intake minus energy expenditure (TDEE).
To lose approximately 0.45 kg (~1 lb) of adipose tissue, a cumulative caloric deficit of approximately 3,500 to 4,000 kcal is required (translating to a daily deficit of 400 to 500 kcal).
However, weight loss is rarely strictly linear over extended timelines due to adaptive thermogenesis (metabolic adaptation), where resting metabolic rate decreases slightly more than predicted by the loss of body mass, accompanied by neuroendocrine reductions in leptin (stimulating appetite) and increases in ghrelin.
Consequently, severe caloric deficits (greater than 25-30% below TDEE or under 1,200 kcal/day for women and 1,500 kcal/day for men) provoke excessive muscle catabolism, thyroid hormone down-regulation, and rebound overeating.
A moderate, patient deficit of 15% to 20% below TDEE, paired with high dietary protein (1.6 to 2.2 g/kg) and resistance training, optimally preserves lean tissue mass and supports long-term fat loss maintenance.
"""
    },
    {
        "title": "Dietary Guidelines for Indians (2024 Revised Edition)",
        "source_name": "Indian Council of Medical Research - National Institute of Nutrition (ICMR-NIN)",
        "author": "ICMR-NIN National Expert Committee on Nutrition",
        "category": "indian_diet",
        "published_year": 2024,
        "url": "https://www.nin.res.in/dietaryguidelines/",
        "content": """
The ICMR-NIN 2024 Dietary Guidelines for Indians emphasize moving away from cereal-heavy carbohydrate diets (traditionally >70% of calories) toward diverse plates rich in pulses, dairy, vegetables, fruits, nuts, and seeds to combat the rising dual burden of undernutrition and non-communicable diseases (diabetes, hypertension, visceral obesity).
Key ICMR-NIN guidelines:
1. Ensure at least 400 to 500 grams of vegetables and whole fresh fruits daily to provide fiber, antioxidants, and essential micronutrients.
2. Include at least 80 to 100 grams of pulses (dal, rajma, chole, soy chunks) or animal proteins daily to meet protein recommendations.
3. Limit added refined cooking oils and fats to less than 20-30 grams per day, choosing cold-pressed mustard, groundnut, or sesame oils, and avoiding re-heated or partially hydrogenated fats (vanaspati).
4. Restrict added refined sugar to under 20-25 grams per day and keep dietary salt intake below 5 grams (1 teaspoon) daily.
5. Emphasize traditional millets (ragi, jowar, bajra) alongside whole wheat and brown rice for sustained glycemic index and satiety.
"""
    }
]

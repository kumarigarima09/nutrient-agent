import { useState, useEffect, useCallback, useMemo } from 'react';
import { mealPlanApi } from '../api/client';

const MEAL_COLORS: Record<string, string> = {
  breakfast: 'var(--accent-orange)',
  mid_morning: 'var(--accent-teal)',
  lunch: 'var(--accent-blue)',
  evening_snack: 'var(--accent-purple)',
  dinner: 'var(--accent-rose)',
  bedtime_snack: 'var(--accent-green)',
};

const MEAL_ICONS: Record<string, string> = {
  breakfast: '🌅',
  mid_morning: '☕',
  lunch: '🍱',
  evening_snack: '🍎',
  dinner: '🌙',
  bedtime_snack: '🥛',
};

type ViewMode = 'daily' | 'weekly' | 'grocery';

export default function MealPlanPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('weekly');

  // Daily state
  const [dailyPlan, setDailyPlan] = useState<any>(null);
  const [dailyLoading, setDailyLoading] = useState(true);
  const [generatingDaily, setGeneratingDaily] = useState(false);

  // Weekly state
  const [weeklyData, setWeeklyData] = useState<any>(null);
  const [weeklyLoading, setWeeklyLoading] = useState(true);
  const [generatingWeekly, setGeneratingWeekly] = useState(false);
  const [selectedDayFilter, setSelectedDayFilter] = useState<string>('all');
  const [collapsedDays, setCollapsedDays] = useState<Record<string, boolean>>({});

  // Grocery state
  const [groceryData, setGroceryData] = useState<any>(null);
  const [groceryLoading, setGroceryLoading] = useState(true);
  const [grocerySearch, setGrocerySearch] = useState('');
  const [groceryCategoryFilter, setGroceryCategoryFilter] = useState('all');
  const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>(() => {
    try {
      const saved = localStorage.getItem('nutri_grocery_checks');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });
  const [copiedNotice, setCopiedNotice] = useState(false);
  const [customItems, setCustomItems] = useState<any[]>(() => {
    try {
      const saved = localStorage.getItem('nutri_custom_grocery');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [showAddCustomModal, setShowAddCustomModal] = useState(false);
  const [newCustomItemName, setNewCustomItemName] = useState('');
  const [newCustomItemQty, setNewCustomItemQty] = useState('');
  const [newCustomItemCategory, setNewCustomItemCategory] = useState('Fresh Vegetables & Greens');

  // Shared actions
  const [loggingSlot, setLoggingSlot] = useState<string | null>(null);
  const [substituteSlot, setSubstituteSlot] = useState<string | null>(null);
  const [subResult, setSubResult] = useState<any>(null);

  // Persist checked items to local storage
  useEffect(() => {
    try {
      localStorage.setItem('nutri_grocery_checks', JSON.stringify(checkedItems));
    } catch { }
  }, [checkedItems]);

  // Persist custom items to local storage
  useEffect(() => {
    try {
      localStorage.setItem('nutri_custom_grocery', JSON.stringify(customItems));
    } catch { }
  }, [customItems]);

  // Load Daily Plan
  const loadDaily = useCallback(async () => {
    setDailyLoading(true);
    try {
      const p = await mealPlanApi.current();
      setDailyPlan(p);
    } catch {
      setDailyPlan(null);
    } finally {
      setDailyLoading(false);
    }
  }, []);

  // Load Weekly Plan Feed
  const loadWeekly = useCallback(async () => {
    setWeeklyLoading(true);
    try {
      const w = await mealPlanApi.getWeekly();
      setWeeklyData(w);
    } catch {
      setWeeklyData(null);
    } finally {
      setWeeklyLoading(false);
    }
  }, []);

  // Load Grocery List
  const loadGrocery = useCallback(async () => {
    setGroceryLoading(true);
    try {
      const g = await mealPlanApi.getGroceryList();
      setGroceryData(g);
    } catch {
      setGroceryData(null);
    } finally {
      setGroceryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDaily();
    loadWeekly();
    loadGrocery();
  }, [loadDaily, loadWeekly, loadGrocery]);

  // Generate handlers
  async function generateDaily() {
    setGeneratingDaily(true);
    try {
      const p = await mealPlanApi.generate();
      setDailyPlan(p);
      loadWeekly();
      loadGrocery();
    } catch { } finally {
      setGeneratingDaily(false);
    }
  }

  async function generateWeekly() {
    setGeneratingWeekly(true);
    try {
      const w = await mealPlanApi.generateWeekly();
      setWeeklyData(w);
      loadDaily();
      loadGrocery();
    } catch { } finally {
      setGeneratingWeekly(false);
    }
  }

  async function logSlot(planId: number, slotName: string, mealTitle?: string) {
    if (!planId) return;
    const key = `${planId}-${slotName}`;
    setLoggingSlot(key);
    try {
      await mealPlanApi.logSlot(planId, slotName);
      alert(`✅ ${mealTitle || slotName.replace(/_/g, ' ')} logged to today's food log!`);
    } catch (e: any) {
      alert(e.message || 'Failed to log meal');
    } finally {
      setLoggingSlot(null);
    }
  }

  async function substitute(foodName: string, calories: number) {
    setSubstituteSlot(foodName);
    setSubResult(null);
    try {
      const res = await mealPlanApi.substitute(foodName, calories);
      setSubResult(res);
    } catch { } finally {
      setSubstituteSlot(null);
    }
  }

  function toggleItemCheck(itemId: string) {
    setCheckedItems(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }));
  }

  function resetChecks() {
    if (confirm('Reset all grocery checkboxes?')) {
      setCheckedItems({});
    }
  }

  function toggleDayCollapse(planDate: string) {
    setCollapsedDays(prev => ({
      ...prev,
      [planDate]: !prev[planDate]
    }));
  }

  function expandAllDays() {
    setCollapsedDays({});
  }

  function collapseAllDays() {
    if (!weeklyData?.days) return;
    const allCollapsed: Record<string, boolean> = {};
    weeklyData.days.forEach((d: any) => {
      allCollapsed[d.plan_date] = true;
    });
    setCollapsedDays(allCollapsed);
  }

  // Copy grocery list formatted for messaging
  function copyGroceryList() {
    if (!groceryData?.categories) return;

    let text = `🛒 *Weekly Grocery List* (${groceryData.start_date} to ${groceryData.end_date})\n\n`;
    groceryData.categories.forEach((cat: any) => {
      const relevant = cat.items.filter((it: any) => !checkedItems[it.id]);
      if (relevant.length > 0) {
        text += `${cat.category_icon} *${cat.category_name}*\n`;
        relevant.forEach((it: any) => {
          text += `  • ${it.food_name}: ${it.display_quantity}\n`;
        });
        text += '\n';
      }
    });

    if (customItems.length > 0) {
      const relevantCustom = customItems.filter((c: any) => !checkedItems[c.id]);
      if (relevantCustom.length > 0) {
        text += `✨ *Extra Items*\n`;
        relevantCustom.forEach((c: any) => {
          text += `  • ${c.food_name}: ${c.display_quantity}\n`;
        });
        text += '\n';
      }
    }

    navigator.clipboard.writeText(text);
    setCopiedNotice(true);
    setTimeout(() => setCopiedNotice(false), 2500);
  }

  function addCustomGroceryItem() {
    if (!newCustomItemName.trim()) return;
    const newItem = {
      id: `custom-${Date.now()}`,
      food_name: newCustomItemName.trim(),
      display_quantity: newCustomItemQty.trim() || '1 item',
      category: newCustomItemCategory,
      is_custom: true,
      days_used: ['Custom'],
      days_count: 1
    };
    setCustomItems(prev => [...prev, newItem]);
    setNewCustomItemName('');
    setNewCustomItemQty('');
    setShowAddCustomModal(false);
  }

  function deleteCustomItem(id: string) {
    setCustomItems(prev => prev.filter(c => c.id !== id));
  }

  // Computed grocery counts & progress
  const allGroceryItemsList = useMemo(() => {
    const list: any[] = [];
    if (groceryData?.categories) {
      groceryData.categories.forEach((cat: any) => {
        cat.items.forEach((it: any) => list.push(it));
      });
    }
    customItems.forEach(c => list.push(c));
    return list;
  }, [groceryData, customItems]);

  const totalGroceryCount = allGroceryItemsList.length;
  const checkedGroceryCount = allGroceryItemsList.filter(it => checkedItems[it.id]).length;
  const groceryProgressPct = totalGroceryCount > 0 ? Math.round((checkedGroceryCount / totalGroceryCount) * 100) : 0;

  // Filtered categories for grocery tab
  const filteredGroceryCategories = useMemo(() => {
    if (!groceryData?.categories) return [];

    return groceryData.categories
      .map((cat: any) => {
        if (groceryCategoryFilter !== 'all' && cat.category_name !== groceryCategoryFilter) {
          return null;
        }

        // Include standard items + custom items for this category
        const catCustom = customItems.filter(c => c.category === cat.category_name);
        const combined = [...cat.items, ...catCustom];

        const matches = combined.filter((it: any) => {
          if (!grocerySearch.trim()) return true;
          return it.food_name.toLowerCase().includes(grocerySearch.toLowerCase().trim());
        });

        if (matches.length === 0) return null;
        return {
          ...cat,
          items: matches
        };
      })
      .filter(Boolean);
  }, [groceryData, customItems, groceryCategoryFilter, grocerySearch]);

  // Daily plan variables
  const dailyMeals: Record<string, any> = dailyPlan?.meals || {};
  const dailyPlanned = dailyPlan?.planned_totals || {};
  const dailyTargets = dailyPlan?.targets || {};
  const dailyTotalCals = dailyPlanned.calories || Object.values(dailyMeals).reduce((s: number, m: any) => s + (m.total_calories || 0), 0);

  // Filtered days for weekly feed
  const displayDays = useMemo(() => {
    if (!weeklyData?.days) return [];
    if (selectedDayFilter === 'all') return weeklyData.days;
    return weeklyData.days.filter((d: any) => d.plan_date === selectedDayFilter || d.short_day?.toLowerCase() === selectedDayFilter.toLowerCase());
  }, [weeklyData, selectedDayFilter]);

  const todayStr = new Date().toISOString().split('T')[0];

  return (
    <div style={{ padding: '32px 36px', maxWidth: 1180, margin: '0 auto', fontFamily: 'Inter,sans-serif' }}>
      {/* Top Header with Navigation Tabs */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 900, letterSpacing: '-0.02em', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 10 }}>
            🥗 Smart Nutrition & Meal Planning
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
            Deterministic meal scheduling, 7-day varied feed, and automated weekly grocery aggregation
          </p>
        </div>

        {/* Tab Controls */}
        <div style={{
          display: 'flex',
          background: 'rgba(255, 255, 255, 0.05)',
          padding: 4,
          borderRadius: 14,
          border: '1px solid var(--border)',
          gap: 4
        }}>
          <button
            id="tab-weekly-feed"
            onClick={() => setViewMode('weekly')}
            style={{
              padding: '8px 18px',
              borderRadius: 'var(--radius-full)',
              fontSize: 13,
              fontWeight: 600,
              fontFamily: 'var(--font-sans)',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: viewMode === 'weekly' ? 'var(--accent-terracotta)' : 'transparent',
              color: viewMode === 'weekly' ? '#ffffff' : 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}
          >
            📋 Weekly Plan Feed
          </button>

          <button
            id="tab-grocery-list"
            onClick={() => setViewMode('grocery')}
            style={{
              padding: '8px 18px',
              borderRadius: 'var(--radius-full)',
              fontSize: 13,
              fontWeight: 600,
              fontFamily: 'var(--font-sans)',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: viewMode === 'grocery' ? 'var(--accent-terracotta)' : 'transparent',
              color: viewMode === 'grocery' ? '#ffffff' : 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}
          >
            🛒 Grocery List
            {totalGroceryCount > 0 && (
              <span style={{
                background: viewMode === 'grocery' ? 'rgba(255,255,255,0.25)' : 'var(--accent-terracotta-subtle)',
                color: viewMode === 'grocery' ? '#ffffff' : 'var(--accent-terracotta)',
                fontSize: 11,
                padding: '1px 7px',
                borderRadius: 'var(--radius-full)',
                fontWeight: 700
              }}>
                {totalGroceryCount}
              </span>
            )}
          </button>

          <button
            id="tab-daily-plan"
            onClick={() => setViewMode('daily')}
            style={{
              padding: '8px 18px',
              borderRadius: 'var(--radius-full)',
              fontSize: 13,
              fontWeight: 600,
              fontFamily: 'var(--font-sans)',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: viewMode === 'daily' ? 'var(--accent-terracotta)' : 'transparent',
              color: viewMode === 'daily' ? '#ffffff' : 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}
          >
            🍽️ Daily Focus
          </button>
        </div>
      </div>

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* VIEW 1: WEEKLY PLAN FEED                                                  */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      {viewMode === 'weekly' && (
        <div>
          {/* Subheader with Action Buttons & Summary */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 14 }}>
            <div>
              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)' }}>
                7-Day Weekly Meal Feed
              </div>
              {weeklyData && (
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 2 }}>
                  Schedule: {weeklyData.start_date} to {weeklyData.end_date} · Avg {Math.round(weeklyData.weekly_average_calories || 0)} kcal/day · {Math.round(weeklyData.weekly_average_protein_g || 0)}g protein/day
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
              <button
                className="btn-secondary"
                style={{ fontSize: 12, padding: '7px 12px' }}
                onClick={expandAllDays}
              >
                Expand All
              </button>
              <button
                className="btn-secondary"
                style={{ fontSize: 12, padding: '7px 12px' }}
                onClick={collapseAllDays}
              >
                Collapse All
              </button>
              <button
                id="btn-generate-weekly"
                className="btn-primary"
                onClick={generateWeekly}
                disabled={generatingWeekly}
                style={{ fontSize: 13, padding: '8px 18px' }}
              >
                {generatingWeekly ? (
                  <><span className="spinner" style={{ width: 14, height: 14 }} /> Generating Week…</>
                ) : (
                  '✨ Regenerate 7-Day Plan'
                )}
              </button>
            </div>
          </div>

          {/* Quick Day Filter Strip */}
          {weeklyData?.days && (
            <div style={{ display: 'flex', gap: 8, marginBottom: 24, overflowX: 'auto', paddingBottom: 6 }}>
              <button
                onClick={() => setSelectedDayFilter('all')}
                style={{
                  padding: '6px 14px',
                  borderRadius: 20,
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: '1px solid',
                  borderColor: selectedDayFilter === 'all' ? 'var(--accent-teal)' : 'var(--border)',
                  background: selectedDayFilter === 'all' ? 'rgba(0, 212, 170, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                  color: selectedDayFilter === 'all' ? 'var(--accent-teal)' : 'var(--text-secondary)',
                  whiteSpace: 'nowrap'
                }}
              >
                All 7 Days
              </button>
              {weeklyData.days.map((day: any) => {
                const isSelected = selectedDayFilter === day.plan_date;
                const isToday = day.plan_date === todayStr;
                return (
                  <button
                    key={day.plan_date}
                    onClick={() => setSelectedDayFilter(day.plan_date)}
                    style={{
                      padding: '6px 14px',
                      borderRadius: 20,
                      fontSize: 12,
                      fontWeight: 600,
                      cursor: 'pointer',
                      border: '1px solid',
                      borderColor: isSelected ? 'var(--accent-teal)' : isToday ? 'var(--accent-blue)' : 'var(--border)',
                      background: isSelected ? 'rgba(0, 212, 170, 0.15)' : isToday ? 'rgba(79, 142, 247, 0.1)' : 'rgba(255, 255, 255, 0.03)',
                      color: isSelected ? 'var(--accent-teal)' : isToday ? 'var(--accent-blue)' : 'var(--text-secondary)',
                      whiteSpace: 'nowrap',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6
                    }}
                  >
                    <span>{day.short_day}</span>
                    <span style={{ fontSize: 10, opacity: 0.7 }}>{day.plan_date.slice(5)}</span>
                    {isToday && <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-blue)' }} />}
                  </button>
                );
              })}
            </div>
          )}

          {/* Loading state */}
          {weeklyLoading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px 0', gap: 14 }}>
              <div className="spinner" style={{ width: 28, height: 28 }} />
              <span style={{ color: 'var(--text-secondary)' }}>Compiling 7-day nutritional feed…</span>
            </div>
          ) : displayDays.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div style={{ fontSize: 54, marginBottom: 16 }}>📋</div>
              <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>No weekly meal plan generated yet</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
                Generate a full week of personalized breakfast, lunch, snack, and dinner schedules.
              </p>
              <button className="btn-primary" onClick={generateWeekly} disabled={generatingWeekly}>
                {generatingWeekly ? 'Generating…' : '✨ Generate 7-Day Plan'}
              </button>
            </div>
          ) : (
            /* Vertical List Feed of Days */
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {displayDays.map((day: any) => {
                const isCollapsed = collapsedDays[day.plan_date];
                const isToday = day.plan_date === todayStr;
                const plannedTotals = day.planned_totals || {};
                const dayMeals = day.meals || {};
                const mealEntries = Object.entries(dayMeals);

                return (
                  <div
                    key={day.plan_date}
                    className="glass-card"
                    style={{
                      padding: 24,
                      border: isToday ? '1px solid rgba(79, 142, 247, 0.4)' : '1px solid var(--border)',
                      boxShadow: isToday ? '0 0 25px rgba(79, 142, 247, 0.1)' : undefined
                    }}
                  >
                    {/* Day Card Header */}
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        cursor: 'pointer',
                        paddingBottom: isCollapsed ? 0 : 16,
                        borderBottom: isCollapsed ? 'none' : '1px solid var(--border)',
                        flexWrap: 'wrap',
                        gap: 12
                      }}
                      onClick={() => toggleDayCollapse(day.plan_date)}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                        <div style={{
                          background: isToday ? 'var(--accent-blue)' : 'rgba(255, 255, 255, 0.08)',
                          color: isToday ? '#fff' : 'var(--text-primary)',
                          borderRadius: 12,
                          padding: '8px 14px',
                          textAlign: 'center',
                          minWidth: 64
                        }}>
                          <div style={{ fontSize: 11, textTransform: 'uppercase', fontWeight: 800, letterSpacing: '0.05em' }}>
                            {day.short_day}
                          </div>
                          <div style={{ fontSize: 16, fontWeight: 900 }}>
                            {day.plan_date.slice(8)}
                          </div>
                        </div>

                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)' }}>
                              {day.day_name}
                            </span>
                            {isToday && (
                              <span className="badge badge-blue" style={{ fontSize: 10, padding: '2px 8px' }}>
                                TODAY
                              </span>
                            )}
                          </div>
                          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                            {day.plan_date} · {mealEntries.length} planned meals
                          </div>
                        </div>
                      </div>

                      {/* Day Macros & Collapse toggle */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                          <span className="badge badge-teal" style={{ fontSize: 12, fontWeight: 700 }}>
                            🔥 {Math.round(plannedTotals.calories || 0)} kcal
                          </span>
                          <span className="badge badge-blue" style={{ fontSize: 12 }}>
                            P: {Math.round(plannedTotals.protein_g || 0)}g
                          </span>
                          <span className="badge badge-orange" style={{ fontSize: 12 }}>
                            C: {Math.round(plannedTotals.carbs_g || 0)}g
                          </span>
                          <span className="badge" style={{ background: 'rgba(167,139,250,0.12)', color: 'var(--accent-purple)', fontSize: 12 }}>
                            F: {Math.round(plannedTotals.fat_g || 0)}g
                          </span>
                        </div>

                        <span style={{ fontSize: 16, color: 'var(--text-muted)', userSelect: 'none' }}>
                          {isCollapsed ? '▼' : '▲'}
                        </span>
                      </div>
                    </div>

                    {/* Meal Slots List inside this day */}
                    {!isCollapsed && (
                      <div style={{ marginTop: 20, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                        {mealEntries.map(([slot, slotData]: [string, any]) => {
                          const color = MEAL_COLORS[slot] || 'var(--accent-teal)';
                          const icon = MEAL_ICONS[slot] || '🍴';
                          const items: any[] = slotData?.items || [];
                          const slotKey = `${day.plan_id}-${slot}`;

                          return (
                            <div
                              key={slot}
                              style={{
                                background: 'rgba(255, 255, 255, 0.025)',
                                border: '1px solid var(--border)',
                                borderRadius: 14,
                                padding: 16,
                                display: 'flex',
                                flexDirection: 'column',
                                justifyContent: 'space-between'
                              }}
                            >
                              <div>
                                {/* Slot Title & Quick Log Button */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <span style={{ fontSize: 20 }}>{icon}</span>
                                    <div>
                                      <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
                                        {slotData?.slot_name || slot.replace(/_/g, ' ')}
                                      </div>
                                      <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
                                        {slotData?.meal_name}
                                      </div>
                                    </div>
                                  </div>

                                  <button
                                    id={`log-${day.plan_id}-${slot}`}
                                    className="btn-secondary"
                                    style={{ fontSize: 11, padding: '4px 10px', whiteSpace: 'nowrap' }}
                                    onClick={() => logSlot(day.plan_id, slot, slotData?.meal_name)}
                                    disabled={loggingSlot === slotKey}
                                    title="Log this meal to today's food intake"
                                  >
                                    {loggingSlot === slotKey ? (
                                      <span className="spinner" style={{ width: 10, height: 10 }} />
                                    ) : (
                                      '+ Log'
                                    )}
                                  </button>
                                </div>

                                {/* Slot Totals */}
                                <div style={{ fontSize: 12, color, fontWeight: 600, marginBottom: 12 }}>
                                  {Math.round(slotData?.total_calories || 0)} kcal · {Math.round(slotData?.total_protein_g || 0)}g protein
                                </div>

                                {/* Ingredients List */}
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 12 }}>
                                  {items.map((item: any, iIdx: number) => (
                                    <div
                                      key={iIdx}
                                      style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        fontSize: 12,
                                        padding: '4px 0',
                                        borderBottom: '1px dashed rgba(255, 255, 255, 0.05)'
                                      }}
                                    >
                                      <span style={{ color: 'var(--text-secondary)' }}>
                                        • {item.food_name} <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>({item.quantity} {item.unit})</span>
                                      </span>
                                      <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                                        {Math.round(item.calories || 0)} kcal
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>

                              {/* Preparation note if available */}
                              {slotData?.preparation_instructions && (
                                <div style={{
                                  fontSize: 11,
                                  color: 'var(--text-muted)',
                                  background: 'rgba(255, 255, 255, 0.02)',
                                  padding: '8px 10px',
                                  borderRadius: 8,
                                  lineHeight: 1.4
                                }}>
                                  📝 {slotData.preparation_instructions}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* VIEW 2: WEEKLY GROCERY LIST                                               */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      {viewMode === 'grocery' && (
        <div>
          {/* Grocery Top Banner */}
          <div className="glass-card" style={{ padding: 24, marginBottom: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 24 }}>🛒</span>
                  <h2 style={{ fontSize: 20, fontWeight: 900, color: 'var(--text-primary)' }}>
                    Aggregated Weekly Grocery Haul
                  </h2>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>
                  All ingredients across all 7 daily meal plans combined into one smart supermarket checklist.
                </p>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <button
                  id="btn-copy-grocery"
                  className="btn-secondary"
                  onClick={copyGroceryList}
                  style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}
                >
                  {copiedNotice ? '✅ Copied to Clipboard!' : '📋 Copy Checklist'}
                </button>

                <button
                  id="btn-add-custom-item"
                  className="btn-primary"
                  onClick={() => setShowAddCustomModal(true)}
                  style={{ fontSize: 12, padding: '8px 14px' }}
                >
                  ➕ Add Custom Item
                </button>

                <button
                  className="btn-secondary"
                  onClick={resetChecks}
                  title="Uncheck all items"
                  style={{ fontSize: 12, padding: '8px 12px' }}
                >
                  🔄 Reset
                </button>
              </div>
            </div>

            {/* Shopping Progress Bar */}
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 8 }}>
                <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Shopping Progress: <strong style={{ color: 'var(--accent-teal)' }}>{checkedGroceryCount}</strong> of <strong>{totalGroceryCount}</strong> items bought
                </span>
                <span style={{ color: 'var(--accent-teal)', fontWeight: 800 }}>
                  {groceryProgressPct}%
                </span>
              </div>
              <div style={{ width: '100%', height: 8, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 10, overflow: 'hidden' }}>
                <div style={{
                  width: `${groceryProgressPct}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, var(--accent-teal), var(--accent-blue))',
                  transition: 'width 0.3s ease',
                  borderRadius: 10
                }} />
              </div>
            </div>
          </div>

          {/* Search & Category Filter Controls */}
          <div style={{ display: 'flex', gap: 14, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
            <input
              id="grocery-search-input"
              type="text"
              className="input-field"
              placeholder="🔍 Search grocery items (e.g. Milk, Spinach, Dal)…"
              value={grocerySearch}
              onChange={e => setGrocerySearch(e.target.value)}
              style={{ maxWidth: 360, fontSize: 13 }}
            />

            {/* Category Filter Pills */}
            <div style={{ display: 'flex', gap: 6, overflowX: 'auto', flexWrap: 'wrap' }}>
              <button
                onClick={() => setGroceryCategoryFilter('all')}
                style={{
                  padding: '6px 12px',
                  borderRadius: 16,
                  fontSize: 12,
                  cursor: 'pointer',
                  border: '1px solid',
                  borderColor: groceryCategoryFilter === 'all' ? 'var(--accent-teal)' : 'var(--border)',
                  background: groceryCategoryFilter === 'all' ? 'rgba(0,212,170,0.15)' : 'rgba(255,255,255,0.02)',
                  color: groceryCategoryFilter === 'all' ? 'var(--accent-teal)' : 'var(--text-secondary)'
                }}
              >
                All Departments
              </button>

              {groceryData?.categories?.map((cat: any) => (
                <button
                  key={cat.category_name}
                  onClick={() => setGroceryCategoryFilter(cat.category_name)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 16,
                    fontSize: 12,
                    cursor: 'pointer',
                    border: '1px solid',
                    borderColor: groceryCategoryFilter === cat.category_name ? 'var(--accent-teal)' : 'var(--border)',
                    background: groceryCategoryFilter === cat.category_name ? 'rgba(0,212,170,0.15)' : 'rgba(255,255,255,0.02)',
                    color: groceryCategoryFilter === cat.category_name ? 'var(--accent-teal)' : 'var(--text-secondary)'
                  }}
                >
                  {cat.category_icon} {cat.category_name.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Grocery Aisle Categories */}
          {groceryLoading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px 0', gap: 14 }}>
              <div className="spinner" style={{ width: 28, height: 28 }} />
              <span style={{ color: 'var(--text-secondary)' }}>Calculating required ingredients…</span>
            </div>
          ) : filteredGroceryCategories.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🛒</div>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>No grocery items found</h3>
              <p style={{ color: 'var(--text-muted)' }}>Try clearing your search query or generate a weekly meal plan first.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 20 }}>
              {filteredGroceryCategories.map((cat: any) => (
                <div key={cat.category_name} className="glass-card" style={{ padding: 20 }}>
                  {/* Category Header */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, paddingBottom: 10, borderBottom: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 20 }}>{cat.category_icon}</span>
                      <h3 style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>
                        {cat.category_name}
                      </h3>
                    </div>
                    <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.06)', color: 'var(--text-secondary)', fontSize: 11 }}>
                      {cat.items.length} items
                    </span>
                  </div>

                  {/* Checklist of Items */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {cat.items.map((it: any) => {
                      const isChecked = !!checkedItems[it.id];

                      return (
                        <div
                          key={it.id}
                          onClick={() => toggleItemCheck(it.id)}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '10px 12px',
                            borderRadius: 10,
                            background: isChecked ? 'rgba(0, 212, 170, 0.04)' : 'rgba(255, 255, 255, 0.02)',
                            border: isChecked ? '1px solid rgba(0, 212, 170, 0.2)' : '1px solid var(--border)',
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                            opacity: isChecked ? 0.6 : 1
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1 }}>
                            {/* Checkbox */}
                            <div style={{
                              width: 18,
                              height: 18,
                              borderRadius: 5,
                              border: isChecked ? '2px solid var(--accent-sage)' : '2px solid var(--border)',
                              background: isChecked ? 'var(--accent-sage)' : 'transparent',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: 11,
                              color: '#ffffff',
                              fontWeight: 900,
                              flexShrink: 0
                            }}>
                              {isChecked && '✓'}
                            </div>

                            <div>
                              <div style={{
                                fontSize: 13,
                                fontWeight: 600,
                                color: isChecked ? 'var(--text-muted)' : 'var(--text-primary)',
                                textDecoration: isChecked ? 'line-through' : 'none'
                              }}>
                                {it.food_name}
                              </div>

                              {/* Days badges */}
                              {it.days_used && it.days_used.length > 0 && (
                                <div style={{ display: 'flex', gap: 4, marginTop: 3 }}>
                                  {it.days_used.slice(0, 4).map((d: string) => (
                                    <span key={d} style={{ fontSize: 9, background: 'rgba(255, 255, 255, 0.06)', padding: '1px 5px', borderRadius: 4, color: 'var(--text-muted)' }}>
                                      {d}
                                    </span>
                                  ))}
                                  {it.days_used.length > 4 && (
                                    <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>
                                      +{it.days_used.length - 4} days
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{
                              fontSize: 12,
                              fontWeight: 700,
                              color: isChecked ? 'var(--text-muted)' : 'var(--accent-teal)',
                              background: 'rgba(0, 212, 170, 0.08)',
                              padding: '3px 8px',
                              borderRadius: 6
                            }}>
                              {it.display_quantity}
                            </span>

                            {it.is_custom && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  deleteCustomItem(it.id);
                                }}
                                style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', fontSize: 12, padding: '2px 4px' }}
                                title="Remove custom item"
                              >
                                ✕
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* VIEW 3: DAILY FOCUS PLAN                                                  */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      {viewMode === 'daily' && (
        <div>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
            <div>
              <h2 style={{ fontSize: 20, fontWeight: 900, marginBottom: 4 }}>
                Today's Nutrition Breakdown
              </h2>
              {dailyPlan && (
                <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                  {new Date(dailyPlan.plan_date || Date.now()).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })} · {Math.round(dailyTotalCals)} kcal planned
                </p>
              )}
            </div>
            <button id="meal-plan-generate" className="btn-primary" onClick={generateDaily} disabled={generatingDaily}>
              {generatingDaily ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Generating…</> : '✨ Generate Single Day'}
            </button>
          </div>

          {/* Targets bar */}
          {dailyTargets.target_calories && (
            <div className="glass-card" style={{ padding: '16px 24px', marginBottom: 24, display: 'flex', gap: 32, flexWrap: 'wrap' }}>
              {[
                { label: 'Target Calories', val: `${Math.round(dailyTargets.target_calories)} kcal`, color: 'var(--accent-teal)' },
                { label: 'Target Protein', val: `${Math.round(dailyTargets.target_protein_g || 0)}g`, color: 'var(--accent-blue)' },
                { label: 'Planned Calories', val: `${Math.round(dailyTotalCals)} kcal`, color: Math.abs(dailyTotalCals - dailyTargets.target_calories) > 150 ? 'var(--accent-rose)' : 'var(--accent-green)' },
                { label: 'Calorie Variance', val: `${dailyPlan?.calorie_variance >= 0 ? '+' : ''}${Math.round(dailyPlan?.calorie_variance || 0)} kcal`, color: 'var(--text-muted)' },
              ].map(s => (
                <div key={s.label}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>{s.label}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: s.color }}>{s.val}</div>
                </div>
              ))}
            </div>
          )}

          {dailyLoading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px 0', gap: 14 }}>
              <div className="spinner" style={{ width: 28, height: 28 }} />
              <span style={{ color: 'var(--text-secondary)' }}>Loading daily plan…</span>
            </div>
          ) : Object.keys(dailyMeals).length === 0 ? (
            <div style={{ textAlign: 'center', paddingTop: 60 }}>
              <div style={{ fontSize: 54, marginBottom: 14 }}>🍽️</div>
              <h3 style={{ fontSize: 20, fontWeight: 800, marginBottom: 10 }}>No active daily plan</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
                Synthesize a balanced day tailored to your calorie and protein goals.
              </p>
              <button className="btn-primary" onClick={generateDaily} disabled={generatingDaily}>
                {generatingDaily ? 'Generating…' : '✨ Generate Daily Plan'}
              </button>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 20 }}>
              {Object.entries(dailyMeals).map(([slot, slotData]: [string, any]) => {
                const color = MEAL_COLORS[slot] || 'var(--accent-teal)';
                const icon = MEAL_ICONS[slot] || '🍴';
                const items: any[] = slotData?.items || [];
                const planId = dailyPlan?.plan_id || dailyPlan?.id;

                return (
                  <div key={slot} className="glass-card" style={{ padding: 22 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontSize: 22 }}>{icon}</span>
                        <div>
                          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', textTransform: 'capitalize' }}>
                            {slotData?.slot_name || slot.replace(/_/g, ' ')}
                          </div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                            {Math.round(slotData?.total_calories || 0)} kcal · {Math.round(slotData?.total_protein_g || 0)}g protein
                          </div>
                          {slotData?.meal_name && (
                            <div style={{ fontSize: 12, color, fontWeight: 600, marginTop: 2 }}>{slotData.meal_name}</div>
                          )}
                        </div>
                      </div>
                      <button
                        id={`log-slot-${slot}`}
                        className="btn-secondary"
                        style={{ fontSize: 12, padding: '6px 12px' }}
                        onClick={() => logSlot(planId, slot, slotData?.meal_name)}
                        disabled={loggingSlot === `${planId}-${slot}`}
                      >
                        {loggingSlot === `${planId}-${slot}` ? <span className="spinner" style={{ width: 12, height: 12 }} /> : '+ Log'}
                      </button>
                    </div>

                    {/* Items */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {items.map((item: any, idx: number) => (
                        <div key={idx} style={{
                          background: 'rgba(255,255,255,0.03)',
                          border: '1px solid var(--border)',
                          borderRadius: 12,
                          padding: '12px 14px',
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                            <div>
                              <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{item.food_name}</div>
                              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{item.serving_description || `${item.quantity} ${item.unit}`}</div>
                            </div>
                            <span style={{ fontSize: 14, fontWeight: 700, color }}>
                              {Math.round(item.calories || 0)} kcal
                            </span>
                          </div>

                          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                            <span className="badge badge-blue">P: {Math.round(item.protein_g || 0)}g</span>
                            <span className="badge badge-orange">C: {Math.round(item.carbs_g || 0)}g</span>
                            <span className="badge" style={{ background: 'rgba(167,139,250,0.12)', color: 'var(--accent-purple)' }}>F: {Math.round(item.fat_g || 0)}g</span>
                          </div>

                          <button
                            id={`substitute-${item.food_name?.replace(/\s/g, '-')}`}
                            onClick={() => substitute(item.food_name, item.calories)}
                            style={{ marginTop: 8, background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 12, cursor: 'pointer', textDecoration: 'underline', padding: 0 }}
                            disabled={substituteSlot === item.food_name}
                          >
                            {substituteSlot === item.food_name ? 'Finding substitute…' : '↔ Find substitute'}
                          </button>
                        </div>
                      ))}
                    </div>

                    {slotData?.preparation_instructions && (
                      <div style={{ marginTop: 12, fontSize: 12, color: 'var(--text-muted)', background: 'rgba(255,255,255,0.02)', padding: '10px 12px', borderRadius: 8, lineHeight: 1.6 }}>
                        📋 {slotData.preparation_instructions}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* MODAL: ADD CUSTOM GROCERY ITEM                                            */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      {showAddCustomModal && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }} onClick={() => setShowAddCustomModal(false)}>
          <div className="glass-card" style={{ maxWidth: 440, width: '90%', padding: 28 }} onClick={e => e.stopPropagation()}>
            <h3 style={{ fontSize: 18, fontWeight: 800, marginBottom: 16 }}>➕ Add Grocery Item</h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                  Item Name
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Extra Virgin Olive Oil, Garlic, Turmeric"
                  value={newCustomItemName}
                  onChange={e => setNewCustomItemName(e.target.value)}
                  autoFocus
                />
              </div>

              <div>
                <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                  Quantity / Pack
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. 1 bottle, 500g, 2 bunches"
                  value={newCustomItemQty}
                  onChange={e => setNewCustomItemQty(e.target.value)}
                />
              </div>

              <div>
                <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                  Department / Aisle
                </label>
                <select
                  className="input-field"
                  value={newCustomItemCategory}
                  onChange={e => setNewCustomItemCategory(e.target.value)}
                >
                  <option value="Fresh Vegetables & Greens">Fresh Vegetables & Greens</option>
                  <option value="Fresh Fruits">Fresh Fruits</option>
                  <option value="Dairy & Plant Alternatives">Dairy & Plant Alternatives</option>
                  <option value="Eggs, Poultry & Seafood">Eggs, Poultry & Seafood</option>
                  <option value="Pulses, Legumes & Plant Proteins">Pulses, Legumes & Plant Proteins</option>
                  <option value="Grains, Breads & Cereals">Grains, Breads & Cereals</option>
                  <option value="Nuts, Seeds & Dry Fruits">Nuts, Seeds & Dry Fruits</option>
                  <option value="Pantry & Seasonings">Pantry & Seasonings</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
                <button className="btn-primary" onClick={addCustomGroceryItem} style={{ flex: 1 }}>
                  Add to List
                </button>
                <button className="btn-secondary" onClick={() => setShowAddCustomModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* MODAL: FOOD SUBSTITUTION RESULT                                           */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      {subResult && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999,
        }} onClick={() => setSubResult(null)}>
          <div className="glass-card" style={{ maxWidth: 460, width: '90%', padding: 28 }} onClick={e => e.stopPropagation()}>
            <h3 style={{ fontSize: 18, fontWeight: 800, marginBottom: 6 }}>↔ Recommended Substitutes</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 16 }}>
              Calibrated to match macronutrients for {subResult.original_food}
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {subResult.substitutes?.map((s: any, i: number) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 10 }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{s.substitute_food}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{s.serving_description || s.fit_note}</div>
                  </div>
                  <span className="badge badge-teal">{Math.round(s.nutrition?.calories || 0)} kcal</span>
                </div>
              ))}
            </div>

            <button className="btn-secondary" onClick={() => setSubResult(null)} style={{ marginTop: 20, width: '100%' }}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  I18nManager,
  StatusBar,
  Linking,
  Platform,
  Animated,
  TextInput,
  Keyboard,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import Constants from 'expo-constants';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

// Force RTL for Arabic
I18nManager.allowRTL(true);
I18nManager.forceRTL(true);

const { width } = Dimensions.get('window');

// API Configuration
const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL ||
                process.env.EXPO_PUBLIC_BACKEND_URL ||
                'https://top5-league-app.preview.emergentagent.com';

// Types
interface League {
  id: string;
  name: string;
  name_en: string;
  tour_id: number;
  comp_id: number;
  country: string;
  logo: string;
}

interface NewsItem {
  id: string;
  title: string;
  summary?: string;
  image_url?: string;
  link: string;
  league_id: string;
  date?: string;
}

interface StandingItem {
  position: number;
  team_name: string;
  team_logo?: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  points: number;
}

interface MatchItem {
  id: string;
  home_team: string;
  away_team: string;
  home_logo?: string;
  away_logo?: string;
  home_score?: number;
  away_score?: number;
  match_time: string;
  match_date: string;
  channel?: string;
  status: string;
  league_id: string;
}

// League colors
const LEAGUE_COLORS: Record<string, string> = {
  'premier-league': '#3D195B',
  'la-liga': '#FF4B44',
  'serie-a': '#024494',
  'bundesliga': '#D20515',
  'ligue-1': '#091C3E',
};

const LEAGUE_FLAGS: Record<string, string> = {
  'premier-league': 'ENG',
  'la-liga': 'ESP',
  'serie-a': 'ITA',
  'bundesliga': 'GER',
  'ligue-1': 'FRA',
};

const DEFAULT_LEAGUES: League[] = [
  { id: 'premier-league', name: 'الإنجليزي', name_en: 'Premier League', tour_id: 93, comp_id: 2968, country: 'إنجلترا', logo: '' },
  { id: 'la-liga', name: 'الإسباني', name_en: 'La Liga', tour_id: 101, comp_id: 2982, country: 'إسبانيا', logo: '' },
  { id: 'serie-a', name: 'الإيطالي', name_en: 'Serie A', tour_id: 100, comp_id: 2981, country: 'إيطاليا', logo: '' },
  { id: 'bundesliga', name: 'الألماني', name_en: 'Bundesliga', tour_id: 98, comp_id: 2980, country: 'ألمانيا', logo: '' },
  { id: 'ligue-1', name: 'الفرنسي', name_en: 'Ligue 1', tour_id: 95, comp_id: 2979, country: 'فرنسا', logo: '' },
];

// Notification Banner Component
const NotificationBanner = ({ notification, onDismiss, color }: { notification: NewsItem | null; onDismiss: () => void; color: string }) => {
  const slideAnim = useRef(new Animated.Value(-120)).current;

  useEffect(() => {
    if (notification) {
      Animated.spring(slideAnim, { toValue: 44, useNativeDriver: true, tension: 80, friction: 10 }).start();
      const timer = setTimeout(() => {
        Animated.timing(slideAnim, { toValue: -120, duration: 300, useNativeDriver: true }).start(() => onDismiss());
      }, 6000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  if (!notification) return null;

  return (
    <Animated.View style={[styles.notificationBanner, { backgroundColor: '#1a1a2e', transform: [{ translateY: slideAnim }] }]}>
      <TouchableOpacity
        testID="notification-banner"
        style={styles.notificationContent}
        onPress={() => { onDismiss(); }}
        activeOpacity={0.8}
      >
        <View style={[styles.notificationIcon, { backgroundColor: color }]}>
          <Ionicons name="flash" size={16} color="#fff" />
        </View>
        <View style={styles.notificationTextWrap}>
          <Text style={styles.notificationLabel}>خبر عاجل</Text>
          <Text style={styles.notificationText} numberOfLines={2}>{notification.title}</Text>
        </View>
        <TouchableOpacity testID="dismiss-notification-btn" onPress={onDismiss} style={styles.notificationClose}>
          <Ionicons name="close" size={16} color="#999" />
        </TouchableOpacity>
      </TouchableOpacity>
    </Animated.View>
  );
};

// Match Card Component
const MatchCard = ({ match, color }: { match: MatchItem; color: string }) => {
  const isFinished = match.status === 'finished';
  const isLive = match.status === 'live';

  return (
    <View testID={`match-card-${match.id}`} style={styles.matchCard}>
      {/* Date & Channel Row */}
      <View style={styles.matchHeader}>
        {match.match_date ? (
          <Text style={styles.matchDate}>{match.match_date}</Text>
        ) : null}
        {isLive && (
          <View style={styles.liveBadgeHeader}>
            <View style={styles.liveDot} />
            <Text style={styles.liveText}>مباشر</Text>
          </View>
        )}
        {isFinished && <Text style={styles.finishedBadge}>انتهت</Text>}
        {match.channel ? (
          <View style={styles.channelBadge}>
            <Ionicons name="tv-outline" size={11} color="#666" />
            <Text style={styles.channelText}>{match.channel}</Text>
          </View>
        ) : null}
      </View>

      {/* Teams Row */}
      <View style={styles.matchTeams}>
        {/* Home Team */}
        <View style={styles.matchTeam}>
          {match.home_logo ? (
            <Image source={{ uri: match.home_logo }} style={styles.matchTeamLogo} resizeMode="contain" />
          ) : (
            <View style={[styles.matchTeamLogoPlaceholder, { backgroundColor: color + '20' }]}>
              <Ionicons name="football-outline" size={20} color={color} />
            </View>
          )}
          <Text style={styles.matchTeamName} numberOfLines={1}>{match.home_team}</Text>
        </View>

        {/* Score/Time */}
        <View style={styles.matchScore}>
          {isFinished || isLive ? (
            <View style={styles.scoreContainer}>
              <Text style={[styles.scoreText, { color }]}>{match.home_score ?? '-'}</Text>
              <Text style={styles.scoreSeparator}>-</Text>
              <Text style={[styles.scoreText, { color }]}>{match.away_score ?? '-'}</Text>
            </View>
          ) : (
            <View style={[styles.timeContainer, { backgroundColor: color + '15' }]}>
              <Text style={[styles.matchTimeText, { color }]}>{match.match_time}</Text>
            </View>
          )}
        </View>

        {/* Away Team */}
        <View style={styles.matchTeam}>
          {match.away_logo ? (
            <Image source={{ uri: match.away_logo }} style={styles.matchTeamLogo} resizeMode="contain" />
          ) : (
            <View style={[styles.matchTeamLogoPlaceholder, { backgroundColor: color + '20' }]}>
              <Ionicons name="football-outline" size={20} color={color} />
            </View>
          )}
          <Text style={styles.matchTeamName} numberOfLines={1}>{match.away_team}</Text>
        </View>
      </View>

      {/* Match Events Summary */}
      {(match as any).scorers_home?.length > 0 || (match as any).scorers_away?.length > 0 || (match as any).cards?.length > 0 ? (
        <View style={styles.matchEventsSection}>
          {/* Scorers */}
          {((match as any).scorers_home || []).map((s: any, i: number) => (
            <View key={`sh${i}`} style={styles.eventRow}>
              <Ionicons name="football" size={12} color="#4CAF50" />
              <Text style={styles.eventText}>{s.player} ({s.time}')</Text>
            </View>
          ))}
          {((match as any).scorers_away || []).map((s: any, i: number) => (
            <View key={`sa${i}`} style={styles.eventRow}>
              <Ionicons name="football" size={12} color="#4CAF50" />
              <Text style={styles.eventText}>{s.player} ({s.time}')</Text>
            </View>
          ))}
          {/* Cards */}
          {((match as any).cards || []).map((c: any, i: number) => (
            <View key={`c${i}`} style={styles.eventRow}>
              <View style={[styles.cardIcon, { backgroundColor: c.type === 'red' ? '#F44336' : '#FFC107' }]} />
              <Text style={styles.eventText}>{c.player} ({c.minute}')</Text>
            </View>
          ))}
        </View>
      ) : null}
    </View>
  );
};

// Setup push notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({ shouldShowAlert: true, shouldPlaySound: true, shouldSetBadge: true }),
});

async function registerForPushNotifications() {
  if (!Device.isDevice) return null;
  try {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== 'granted') return null;
    const tokenData = await Notifications.getExpoPushTokenAsync({ projectId: Constants.expoConfig?.extra?.eas?.projectId });
    // Register token with backend
    try {
      await fetch(`${API_URL}/api/register-push-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: tokenData.data }),
      });
    } catch {}
    return tokenData.data;
  } catch { return null; }
}

export default function HomeScreen() {
  const router = useRouter();
  const [selectedLeague, setSelectedLeague] = useState<string>('premier-league');
  const [activeTab, setActiveTab] = useState<'news' | 'standings' | 'matches'>('news');
  const [leagues] = useState<League[]>(DEFAULT_LEAGUES);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [standings, setStandings] = useState<StandingItem[]>([]);
  const [matches, setMatches] = useState<MatchItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notification, setNotification] = useState<NewsItem | null>(null);
  const [seenNewsIds, setSeenNewsIds] = useState<Set<string>>(new Set());
  const notifTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<NewsItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [newsCounts, setNewsCounts] = useState<Record<string, number>>({});
  const [readNewsIds, setReadNewsIds] = useState<Set<string>>(new Set());
  const [syncing, setSyncing] = useState(false);
  const spinAnim = useRef(new Animated.Value(0)).current;

  // Register push notifications on mount
  useEffect(() => {
    registerForPushNotifications();
    fetchNewsCounts();
  }, []);

  // Fetch news counts for all leagues
  const fetchNewsCounts = async () => {
    try {
      const res = await fetch(`${API_URL}/api/news-counts`);
      if (res.ok) {
        const data = await res.json();
        setNewsCounts(data.counts || {});
      }
    } catch {}
  };

  // Sync all data
  const handleSync = async () => {
    setSyncing(true);
    Animated.loop(Animated.timing(spinAnim, { toValue: 1, duration: 800, useNativeDriver: true })).start();
    try {
      await fetchNewsCounts();
      if (activeTab === 'news') await fetchNews(selectedLeague);
      else if (activeTab === 'standings') await fetchStandings(selectedLeague);
      else await fetchMatches(selectedLeague);
    } finally {
      setSyncing(false);
      spinAnim.setValue(0);
    }
  };

  const spinInterpolate = spinAnim.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '360deg'] });

  // Fetch news
  const fetchNews = async (leagueId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/news/${leagueId}`);
      if (response.ok) {
        const data = await response.json();
        const items = data.news || [];
        setNews(items);
        // Check for new news for notifications
        if (items.length > 0 && seenNewsIds.size > 0) {
          const newItem = items.find((n: NewsItem) => !seenNewsIds.has(n.title));
          if (newItem) {
            setNotification(newItem);
          }
        }
        // Mark all as seen
        const newSeen = new Set(seenNewsIds);
        items.forEach((n: NewsItem) => newSeen.add(n.title));
        setSeenNewsIds(newSeen);
      } else {
        setError('فشل في تحميل الأخبار');
      }
    } catch {
      setError('خطأ في الاتصال بالخادم');
    } finally {
      setLoading(false);
    }
  };

  // Fetch standings
  const fetchStandings = async (leagueId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/standings/${leagueId}`);
      if (response.ok) {
        const data = await response.json();
        setStandings(data.standings || []);
      } else {
        setError('فشل في تحميل الترتيب');
      }
    } catch {
      setError('خطأ في الاتصال بالخادم');
    } finally {
      setLoading(false);
    }
  };

  // Fetch matches
  const fetchMatches = async (leagueId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/matches/${leagueId}`);
      if (response.ok) {
        const data = await response.json();
        setMatches(data.matches || []);
      } else {
        setError('فشل في تحميل المباريات');
      }
    } catch {
      setError('خطأ في الاتصال بالخادم');
    } finally {
      setLoading(false);
    }
  };

  // Load data based on tab
  useEffect(() => {
    if (activeTab === 'news') fetchNews(selectedLeague);
    else if (activeTab === 'standings') fetchStandings(selectedLeague);
    else fetchMatches(selectedLeague);
  }, [selectedLeague, activeTab]);

  // Auto-refresh notifications every 5 minutes
  useEffect(() => {
    notifTimerRef.current = setInterval(() => {
      fetchNews(selectedLeague);
    }, 300000); // 5 min
    return () => { if (notifTimerRef.current) clearInterval(notifTimerRef.current); };
  }, [selectedLeague]);

  // Pull to refresh
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    if (activeTab === 'news') await fetchNews(selectedLeague);
    else if (activeTab === 'standings') await fetchStandings(selectedLeague);
    else await fetchMatches(selectedLeague);
    setRefreshing(false);
  }, [selectedLeague, activeTab]);

  // Search news
  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.length < 2) { setSearchResults([]); setIsSearching(false); return; }
    setIsSearching(true);
    try {
      const res = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}&league_id=${selectedLeague}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.results || []);
      }
    } catch {} finally { setIsSearching(false); }
  };

  // Navigate to news detail + mark as read
  const openNewsDetail = (item: NewsItem) => {
    // Mark as read and decrement count
    if (!readNewsIds.has(item.id)) {
      const newRead = new Set(readNewsIds);
      newRead.add(item.id);
      setReadNewsIds(newRead);
      // Decrement the news count for this league
      const lid = item.league_id || selectedLeague;
      setNewsCounts(prev => ({ ...prev, [lid]: Math.max((prev[lid] || 0) - 1, 0) }));
    }
    router.push({
      pathname: '/news-detail',
      params: {
        id: item.id,
        title: item.title,
        image_url: item.image_url || '',
        link: item.link,
        league_id: item.league_id || selectedLeague,
        date: item.date || '',
      },
    });
  };

  const currentColor = LEAGUE_COLORS[selectedLeague] || '#1a5f2a';

  // --- RENDER FUNCTIONS ---

  const renderLeagueSelector = () => (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.leagueSelectorContent} style={styles.leagueSelector}>
      {leagues.map((league) => {
        const isSelected = selectedLeague === league.id;
        const leagueColor = LEAGUE_COLORS[league.id] || '#333';
        return (
          <TouchableOpacity
            key={league.id}
            testID={`league-btn-${league.id}`}
            style={[styles.leagueButton, isSelected && { backgroundColor: leagueColor, borderColor: leagueColor }]}
            onPress={() => setSelectedLeague(league.id)}
          >
            <Text style={[styles.leagueCountryCode, isSelected && { color: '#fff' }]}>{LEAGUE_FLAGS[league.id]}</Text>
            <Text style={[styles.leagueButtonText, isSelected && styles.leagueButtonTextActive]}>{league.name}</Text>
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );

  const renderTabSelector = () => (
    <View style={styles.tabContainer}>
      {([
        { key: 'news' as const, label: 'الأخبار', icon: 'newspaper-outline' as const },
        { key: 'standings' as const, label: 'الترتيب', icon: 'trophy-outline' as const },
        { key: 'matches' as const, label: 'المباريات', icon: 'football-outline' as const },
      ]).map((tab) => (
        <TouchableOpacity
          key={tab.key}
          testID={`tab-${tab.key}`}
          style={[styles.tab, activeTab === tab.key && { backgroundColor: currentColor }]}
          onPress={() => setActiveTab(tab.key)}
        >
          <Ionicons name={tab.icon} size={18} color={activeTab === tab.key ? '#fff' : '#888'} />
          <Text style={[styles.tabText, activeTab === tab.key && styles.tabTextActive]}>{tab.label}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderNewsItem = (item: NewsItem) => (
    <TouchableOpacity
      key={item.id}
      testID={`news-card-${item.id}`}
      style={styles.newsCard}
      onPress={() => openNewsDetail(item)}
      activeOpacity={0.8}
    >
      {item.image_url ? (
        <Image source={{ uri: item.image_url }} style={styles.newsImage} resizeMode="cover" />
      ) : (
        <View style={[styles.newsImagePlaceholder, { backgroundColor: currentColor + '15' }]}>
          <Ionicons name="newspaper-outline" size={40} color={currentColor} />
        </View>
      )}
      <View style={styles.newsContent}>
        <Text style={styles.newsTitle} numberOfLines={3}>{item.title}</Text>
        {item.date ? <Text style={styles.newsDate}>{item.date}</Text> : null}
      </View>
    </TouchableOpacity>
  );

  const renderStandings = () => (
    <View testID="standings-table" style={styles.standingsContainer}>
      <View style={[styles.standingsRow, styles.standingsHeader, { backgroundColor: currentColor }]}>
        <Text style={[styles.standingsCell, styles.headerText, { flex: 0.4 }]}>#</Text>
        <Text style={[styles.standingsCell, styles.headerText, { flex: 2.5, textAlign: 'right' }]}>الفريق</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>لعب</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>ف</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>ت</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>خ</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>له</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>عليه</Text>
        <Text style={[styles.standingsCell, styles.headerText, { fontWeight: '900' }]}>نقاط</Text>
      </View>
      {standings.map((team, index) => {
        const isTop4 = team.position <= 4;
        const isBottom3 = team.position >= standings.length - 2;
        return (
          <View
            key={`${team.team_name}-${index}`}
            testID={`standing-row-${team.position}`}
            style={[
              styles.standingsRow,
              index % 2 === 0 ? styles.evenRow : styles.oddRow,
              isTop4 && { borderRightWidth: 3, borderRightColor: '#4CAF50' },
              isBottom3 && { borderRightWidth: 3, borderRightColor: '#F44336' },
            ]}
          >
            <Text style={[styles.standingsCell, { flex: 0.4, fontWeight: 'bold', color: isTop4 ? '#4CAF50' : isBottom3 ? '#F44336' : '#333' }]}>{team.position}</Text>
            <View style={[styles.teamCell, { flex: 2.5 }]}>
              {team.team_logo ? (
                <Image source={{ uri: team.team_logo }} style={styles.teamLogo} resizeMode="contain" />
              ) : null}
              <Text style={styles.teamName} numberOfLines={1}>{team.team_name}</Text>
            </View>
            <Text style={styles.standingsCell}>{team.played}</Text>
            <Text style={[styles.standingsCell, { color: '#4CAF50' }]}>{team.won}</Text>
            <Text style={[styles.standingsCell, { color: '#FF9800' }]}>{team.drawn}</Text>
            <Text style={[styles.standingsCell, { color: '#F44336' }]}>{team.lost}</Text>
            <Text style={styles.standingsCell}>{team.goals_for}</Text>
            <Text style={styles.standingsCell}>{team.goals_against}</Text>
            <Text style={[styles.standingsCell, styles.pointsCell, { color: currentColor }]}>{team.points}</Text>
          </View>
        );
      })}
      <View style={styles.standingsLegend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#4CAF50' }]} />
          <Text style={styles.legendText}>دوري الأبطال</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#F44336' }]} />
          <Text style={styles.legendText}>هبوط</Text>
        </View>
      </View>
    </View>
  );

  const renderMatches = () => (
    <View testID="matches-list" style={styles.matchesContainer}>
      {matches.length === 0 ? (
        <View style={styles.centerContainer}>
          <Ionicons name="football-outline" size={48} color="#999" />
          <Text style={styles.emptyText}>لا توجد مباريات متاحة</Text>
        </View>
      ) : (
        matches.map((match) => <MatchCard key={match.id} match={match} color={currentColor} />)
      )}
    </View>
  );

  const renderContent = () => {
    if (loading) {
      return (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={currentColor} />
          <Text style={styles.loadingText}>جاري التحميل...</Text>
        </View>
      );
    }
    if (error) {
      return (
        <View style={styles.centerContainer}>
          <Ionicons name="alert-circle-outline" size={48} color="#d32f2f" />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity testID="retry-btn" style={[styles.retryButton, { backgroundColor: currentColor }]} onPress={onRefresh}>
            <Text style={styles.retryButtonText}>إعادة المحاولة</Text>
          </TouchableOpacity>
        </View>
      );
    }
    if (activeTab === 'news') {
      // Show search results if searching
      const displayNews = searchQuery.length >= 2 ? searchResults : news;
      if (displayNews.length === 0) {
        const emptyMsg = searchQuery.length >= 2 ? `لا توجد نتائج لـ "${searchQuery}"` : 'لا توجد أخبار متاحة';
        return <View style={styles.centerContainer}><Ionicons name="newspaper-outline" size={48} color="#999" /><Text style={styles.emptyText}>{emptyMsg}</Text></View>;
      }
      if (searchQuery.length >= 2) {
        return <View><Text style={styles.searchResultsCount}>نتائج البحث: {searchResults.length}</Text>{displayNews.map(renderNewsItem)}</View>;
      }
      return <View>{displayNews.map(renderNewsItem)}</View>;
    }
    if (activeTab === 'standings') {
      if (standings.length === 0) return <View style={styles.centerContainer}><Ionicons name="trophy-outline" size={48} color="#999" /><Text style={styles.emptyText}>لا يوجد ترتيب متاح</Text></View>;
      return renderStandings();
    }
    return renderMatches();
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />

      {/* Notification Banner */}
      <NotificationBanner notification={notification} onDismiss={() => setNotification(null)} color={currentColor} />

      {/* Header */}
      <View style={[styles.header, { backgroundColor: '#1a1a2e' }]}>
        <View style={styles.headerRow}>
          <TouchableOpacity testID="search-toggle-btn" onPress={() => { setShowSearch(!showSearch); if (showSearch) { setSearchQuery(''); setSearchResults([]); Keyboard.dismiss(); } }} style={styles.searchToggleBtn}>
            <Ionicons name={showSearch ? 'close' : 'search'} size={20} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>أخبار الدوريات الأوروبية</Text>
          <TouchableOpacity testID="sync-btn" onPress={handleSync} style={styles.syncBtn} disabled={syncing}>
            <Animated.View style={{ transform: [{ rotate: syncing ? spinInterpolate : '0deg' }] }}>
              <Ionicons name="sync" size={20} color="#fff" />
            </Animated.View>
          </TouchableOpacity>
        </View>
        {showSearch && (
          <View style={styles.searchBar}>
            <Ionicons name="search" size={18} color="#999" />
            <TextInput
              testID="search-input"
              style={styles.searchInput}
              placeholder="ابحث في الأخبار..."
              placeholderTextColor="#999"
              value={searchQuery}
              onChangeText={handleSearch}
              autoFocus
              returnKeyType="search"
            />
            {isSearching && <ActivityIndicator size="small" color="#fff" />}
            {searchQuery.length > 0 && !isSearching && (
              <TouchableOpacity onPress={() => { setSearchQuery(''); setSearchResults([]); }}>
                <Ionicons name="close-circle" size={18} color="#ccc" />
              </TouchableOpacity>
            )}
          </View>
        )}
      </View>

      {/* League Top Menu */}
      <View style={[styles.leagueTopMenu, { backgroundColor: '#1a1a2e' }]}>
        {leagues.map((league) => {
          const isSelected = selectedLeague === league.id;
          const leagueColor = LEAGUE_COLORS[league.id] || '#fff';
          return (
            <TouchableOpacity
              key={league.id}
              testID={`league-btn-${league.id}`}
              style={[styles.leagueTopItem, isSelected && styles.leagueTopItemActive]}
              onPress={() => setSelectedLeague(league.id)}
            >
              <View style={[styles.leagueDot, { backgroundColor: leagueColor }]} />
              <Text style={[styles.leagueTopText, isSelected && styles.leagueTopTextActive]}>{league.name}</Text>
              {(newsCounts[league.id] || 0) > 0 && (
                <View style={styles.newsCountBadge}>
                  <Text style={styles.newsCountText}>{newsCounts[league.id]}</Text>
                </View>
              )}
              {isSelected && <View style={styles.leagueTopIndicator} />}
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Tab Selector */}
      {renderTabSelector()}

      {/* Content */}
      <ScrollView
        style={styles.content}
        contentContainerStyle={styles.contentContainer}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[currentColor]} tintColor={currentColor} />}
      >
        {renderContent()}
        {/* Ad Banner Placeholder */}
        <View testID="ad-banner" style={styles.adBanner}>
          <Text style={styles.adBannerLabel}>AD</Text>
          <Text style={styles.adBannerText}>إعلان</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f2f2f7' },

  // Header
  header: { paddingHorizontal: 16, paddingTop: 10, paddingBottom: 8 },
  headerRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#fff', textAlign: 'center', flex: 1 },
  headerSubtitle: { fontSize: 12, color: 'rgba(255,255,255,0.7)', marginTop: 2, marginRight: 34 },
  searchToggleBtn: { padding: 6, backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 20 },
  searchBar: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 6, marginTop: 10, gap: 8 },
  searchInput: { flex: 1, fontSize: 14, color: '#fff', textAlign: 'right', paddingVertical: 4 },
  searchResultsCount: { fontSize: 13, color: '#888', textAlign: 'right', marginBottom: 10, fontWeight: '600' },

  // League Top Menu
  leagueTopMenu: { flexDirection: 'row', paddingBottom: 0 },
  leagueTopItem: { flex: 1, alignItems: 'center', paddingVertical: 10, position: 'relative' as const, gap: 3 },
  leagueTopItemActive: {},
  leagueDot: { width: 8, height: 8, borderRadius: 4 },
  leagueTopText: { fontSize: 11, color: 'rgba(255,255,255,0.45)', fontWeight: '600' },
  leagueTopFlag: { fontSize: 10, fontWeight: '900', color: 'rgba(255,255,255,0.4)', backgroundColor: 'rgba(255,255,255,0.1)', paddingHorizontal: 5, paddingVertical: 1, borderRadius: 4, overflow: 'hidden' as const },
  leagueTopTextActive: { color: '#fff', fontWeight: 'bold' },
  leagueTopIndicator: { position: 'absolute' as const, bottom: 0, left: '15%' as any, right: '15%' as any, height: 3, backgroundColor: '#FFD700', borderTopLeftRadius: 2, borderTopRightRadius: 2 },

  // League Selector
  leagueSelector: { backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e5ea' },
  leagueSelectorContent: { paddingHorizontal: 8, paddingVertical: 10 },
  leagueButton: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 8, marginHorizontal: 4, borderRadius: 20, borderWidth: 1.5, borderColor: '#ddd', backgroundColor: '#f9f9f9', gap: 6 },
  leagueCountryCode: { fontSize: 11, fontWeight: '800', color: '#888' },
  leagueButtonText: { fontSize: 13, color: '#333', fontWeight: '600' },
  leagueButtonTextActive: { color: '#fff' },

  // Tabs
  tabContainer: { flexDirection: 'row', backgroundColor: '#fff', paddingHorizontal: 12, paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#e5e5ea', gap: 6 },
  tab: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 10, borderRadius: 10, backgroundColor: '#f0f0f5', gap: 5 },
  tabText: { fontSize: 13, color: '#888', fontWeight: '600' },
  tabTextActive: { color: '#fff', fontWeight: 'bold' },

  // Content
  content: { flex: 1 },
  contentContainer: { padding: 12, paddingBottom: 32 },
  centerContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: 60 },
  loadingText: { marginTop: 12, fontSize: 14, color: '#666' },
  errorText: { marginTop: 12, fontSize: 14, color: '#d32f2f', textAlign: 'center' },
  emptyText: { marginTop: 12, fontSize: 14, color: '#999' },
  retryButton: { marginTop: 16, paddingHorizontal: 24, paddingVertical: 10, borderRadius: 20 },
  retryButtonText: { color: '#fff', fontWeight: 'bold' },

  // News
  newsCard: { backgroundColor: '#fff', borderRadius: 14, overflow: 'hidden', marginBottom: 14, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.08, shadowRadius: 8, elevation: 3 },
  newsImage: { width: '100%', height: 190, backgroundColor: '#e5e5ea' },
  newsImagePlaceholder: { width: '100%', height: 120, alignItems: 'center', justifyContent: 'center' },
  newsContent: { padding: 14 },
  newsTitle: { fontSize: 15, fontWeight: '700', color: '#1c1c1e', lineHeight: 24, textAlign: 'right' },
  newsDate: { marginTop: 8, fontSize: 12, color: '#8e8e93', textAlign: 'right' },

  // Standings
  standingsContainer: { backgroundColor: '#fff', borderRadius: 14, overflow: 'hidden', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.08, shadowRadius: 8, elevation: 3 },
  standingsRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, paddingHorizontal: 6, borderBottomWidth: 0.5, borderBottomColor: '#e5e5ea' },
  standingsHeader: { paddingVertical: 12 },
  headerText: { color: '#fff', fontWeight: 'bold', fontSize: 11 },
  evenRow: { backgroundColor: '#fff' },
  oddRow: { backgroundColor: '#fafafa' },
  standingsCell: { flex: 1, fontSize: 12, textAlign: 'center', color: '#333' },
  teamCell: { flexDirection: 'row', alignItems: 'center' },
  teamLogo: { width: 22, height: 22, marginLeft: 6 },
  teamName: { fontSize: 12, color: '#333', flex: 1, textAlign: 'right' },
  pointsCell: { fontWeight: '900', fontSize: 13 },
  standingsLegend: { flexDirection: 'row', justifyContent: 'center', paddingVertical: 10, gap: 20 },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  legendDot: { width: 8, height: 8, borderRadius: 4 },
  legendText: { fontSize: 11, color: '#8e8e93' },

  // Matches
  matchesContainer: { gap: 12 },
  matchCard: { backgroundColor: '#fff', borderRadius: 14, padding: 14, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.08, shadowRadius: 8, elevation: 3, marginBottom: 12 },
  matchHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, paddingBottom: 8, borderBottomWidth: 0.5, borderBottomColor: '#e5e5ea' },
  matchDate: { fontSize: 11, color: '#8e8e93' },
  channelBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: '#f2f2f7', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10 },
  channelText: { fontSize: 10, color: '#666' },
  matchTeams: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  matchTeam: { flex: 1, alignItems: 'center', gap: 8 },
  matchTeamLogo: { width: 44, height: 44 },
  matchTeamLogoPlaceholder: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' },
  matchTeamName: { fontSize: 12, fontWeight: '600', color: '#333', textAlign: 'center' },
  matchScore: { alignItems: 'center', paddingHorizontal: 12 },
  scoreContainer: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  scoreText: { fontSize: 28, fontWeight: '900' },
  scoreSeparator: { fontSize: 20, color: '#ccc', fontWeight: '300' },
  timeContainer: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8 },
  matchTimeText: { fontSize: 16, fontWeight: '800' },
  liveBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 },
  liveDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#F44336' },
  liveText: { fontSize: 10, color: '#F44336', fontWeight: 'bold' },
  finishedText: { fontSize: 10, color: '#8e8e93', marginTop: 4 },
  finishedBadge: { fontSize: 10, color: '#8e8e93', backgroundColor: '#f0f0f5', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8 },
  liveBadgeHeader: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: 'rgba(244,67,54,0.1)', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8 },

  // Match Events
  matchEventsSection: { borderTopWidth: 0.5, borderTopColor: '#e5e5ea', marginTop: 10, paddingTop: 8, gap: 4 },
  eventRow: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 2 },
  eventText: { fontSize: 11, color: '#666', textAlign: 'right' },
  cardIcon: { width: 10, height: 14, borderRadius: 2 },

  // Notification - looks like system push notification
  notificationBanner: { position: 'absolute', top: 0, left: 8, right: 8, zIndex: 999, borderRadius: 14, overflow: 'hidden' as const, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 12, elevation: 10 },
  notificationContent: { flexDirection: 'row', alignItems: 'center', padding: 14 },
  notificationIcon: { width: 36, height: 36, borderRadius: 10, backgroundColor: 'rgba(255,255,255,0.2)', alignItems: 'center', justifyContent: 'center', marginLeft: 10 },
  notificationTextWrap: { flex: 1 },
  notificationLabel: { fontSize: 11, fontWeight: '800', color: '#FFD700', marginBottom: 2 },
  notificationText: { fontSize: 13, color: '#fff', fontWeight: '600', lineHeight: 20 },
  notificationClose: { padding: 8 },

  // Sync Button
  syncBtn: { padding: 6, backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 20 },

  // News Count Badge
  newsCountBadge: { position: 'absolute', top: 2, right: 4, backgroundColor: '#FF3B30', borderRadius: 8, minWidth: 16, height: 16, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 3 },
  newsCountText: { fontSize: 9, color: '#fff', fontWeight: 'bold' },

  // Ad Banner
  adBanner: { backgroundColor: '#f0f0f5', borderRadius: 10, paddingVertical: 14, alignItems: 'center', justifyContent: 'center', marginTop: 16, borderWidth: 1, borderColor: '#e0e0e0', borderStyle: 'dashed' },
  adBannerLabel: { fontSize: 10, color: '#aaa', fontWeight: 'bold', letterSpacing: 1 },
  adBannerText: { fontSize: 12, color: '#bbb', marginTop: 2 },
});

import React, { useState, useEffect, useCallback } from 'react';
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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

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

// League data with colors
const LEAGUE_COLORS: Record<string, string> = {
  'premier-league': '#3D195B',
  'la-liga': '#FF4B44',
  'serie-a': '#024494',
  'bundesliga': '#D20515',
  'ligue-1': '#091C3E',
};

const DEFAULT_LEAGUES: League[] = [
  {
    id: 'premier-league',
    name: 'الدوري الإنجليزي',
    name_en: 'Premier League',
    tour_id: 93,
    comp_id: 2968,
    country: 'إنجلترا',
    logo: 'https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg'
  },
  {
    id: 'la-liga',
    name: 'الدوري الإسباني',
    name_en: 'La Liga',
    tour_id: 95,
    comp_id: 2978,
    country: 'إسبانيا',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/1/13/LaLiga.svg'
  },
  {
    id: 'serie-a',
    name: 'الدوري الإيطالي',
    name_en: 'Serie A',
    tour_id: 94,
    comp_id: 2981,
    country: 'إيطاليا',
    logo: 'https://upload.wikimedia.org/wikipedia/en/e/e1/Serie_A_logo_%282019%29.svg'
  },
  {
    id: 'bundesliga',
    name: 'الدوري الألماني',
    name_en: 'Bundesliga',
    tour_id: 92,
    comp_id: 2980,
    country: 'ألمانيا',
    logo: 'https://upload.wikimedia.org/wikipedia/en/d/df/Bundesliga_logo_%282017%29.svg'
  },
  {
    id: 'ligue-1',
    name: 'الدوري الفرنسي',
    name_en: 'Ligue 1',
    tour_id: 96,
    comp_id: 2979,
    country: 'فرنسا',
    logo: 'https://upload.wikimedia.org/wikipedia/en/4/4c/Ligue1.svg'
  },
];

export default function HomeScreen() {
  const [selectedLeague, setSelectedLeague] = useState<string>('premier-league');
  const [activeTab, setActiveTab] = useState<'news' | 'standings'>('news');
  const [leagues, setLeagues] = useState<League[]>(DEFAULT_LEAGUES);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [standings, setStandings] = useState<StandingItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch leagues from API
  const fetchLeagues = async () => {
    try {
      const response = await fetch(`${API_URL}/api/leagues`);
      if (response.ok) {
        const data = await response.json();
        if (data && data.length > 0) {
          setLeagues(data);
        }
      }
    } catch (err) {
      console.log('Using default leagues');
    }
  };

  // Fetch news for selected league
  const fetchNews = async (leagueId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/news/${leagueId}`);
      if (response.ok) {
        const data = await response.json();
        setNews(data.news || []);
      } else {
        setError('فشل في تحميل الأخبار');
      }
    } catch (err) {
      setError('خطأ في الاتصال بالخادم');
      console.error('Error fetching news:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch standings for selected league
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
    } catch (err) {
      setError('خطأ في الاتصال بالخادم');
      console.error('Error fetching standings:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchLeagues();
  }, []);

  // Load data when league or tab changes
  useEffect(() => {
    if (activeTab === 'news') {
      fetchNews(selectedLeague);
    } else {
      fetchStandings(selectedLeague);
    }
  }, [selectedLeague, activeTab]);

  // Pull to refresh
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    if (activeTab === 'news') {
      await fetchNews(selectedLeague);
    } else {
      await fetchStandings(selectedLeague);
    }
    setRefreshing(false);
  }, [selectedLeague, activeTab]);

  // Open news link
  const openNewsLink = (url: string) => {
    Linking.openURL(url).catch(err => console.error('Error opening URL:', err));
  };

  // Get current league color
  const currentColor = LEAGUE_COLORS[selectedLeague] || '#1a5f2a';

  // Render league selector
  const renderLeagueSelector = () => (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.leagueSelectorContent}
      style={styles.leagueSelector}
    >
      {leagues.map((league) => (
        <TouchableOpacity
          key={league.id}
          style={[
            styles.leagueButton,
            selectedLeague === league.id && {
              backgroundColor: LEAGUE_COLORS[league.id] || '#1a5f2a',
              borderColor: LEAGUE_COLORS[league.id] || '#1a5f2a',
            },
          ]}
          onPress={() => setSelectedLeague(league.id)}
        >
          <Text
            style={[
              styles.leagueButtonText,
              selectedLeague === league.id && styles.leagueButtonTextActive,
            ]}
          >
            {league.name}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  // Render tab selector
  const renderTabSelector = () => (
    <View style={styles.tabContainer}>
      <TouchableOpacity
        style={[
          styles.tab,
          activeTab === 'news' && { backgroundColor: currentColor },
        ]}
        onPress={() => setActiveTab('news')}
      >
        <Ionicons
          name="newspaper-outline"
          size={20}
          color={activeTab === 'news' ? '#fff' : '#666'}
        />
        <Text
          style={[
            styles.tabText,
            activeTab === 'news' && styles.tabTextActive,
          ]}
        >
          الأخبار
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[
          styles.tab,
          activeTab === 'standings' && { backgroundColor: currentColor },
        ]}
        onPress={() => setActiveTab('standings')}
      >
        <Ionicons
          name="trophy-outline"
          size={20}
          color={activeTab === 'standings' ? '#fff' : '#666'}
        />
        <Text
          style={[
            styles.tabText,
            activeTab === 'standings' && styles.tabTextActive,
          ]}
        >
          الترتيب
        </Text>
      </TouchableOpacity>
    </View>
  );

  // Render news item
  const renderNewsItem = (item: NewsItem) => (
    <TouchableOpacity
      key={item.id}
      style={styles.newsCard}
      onPress={() => openNewsLink(item.link)}
      activeOpacity={0.8}
    >
      {item.image_url && (
        <Image
          source={{ uri: item.image_url }}
          style={styles.newsImage}
          resizeMode="cover"
        />
      )}
      <View style={styles.newsContent}>
        <Text style={styles.newsTitle} numberOfLines={3}>
          {item.title}
        </Text>
        {item.date && (
          <Text style={styles.newsDate}>{item.date}</Text>
        )}
      </View>
    </TouchableOpacity>
  );

  // Render standings table
  const renderStandings = () => (
    <View style={styles.standingsContainer}>
      {/* Table Header */}
      <View style={[styles.standingsRow, styles.standingsHeader, { backgroundColor: currentColor }]}>
        <Text style={[styles.standingsCell, styles.headerText, { flex: 0.5 }]}>#</Text>
        <Text style={[styles.standingsCell, styles.headerText, { flex: 2, textAlign: 'right' }]}>الفريق</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>لعب</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>ف</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>ت</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>خ</Text>
        <Text style={[styles.standingsCell, styles.headerText]}>نقاط</Text>
      </View>
      {/* Table Body */}
      {standings.map((team, index) => (
        <View
          key={`${team.team_name}-${index}`}
          style={[
            styles.standingsRow,
            index % 2 === 0 ? styles.evenRow : styles.oddRow,
          ]}
        >
          <Text style={[styles.standingsCell, { flex: 0.5, fontWeight: 'bold' }]}>
            {team.position}
          </Text>
          <View style={[styles.teamCell, { flex: 2 }]}>
            {team.team_logo && (
              <Image
                source={{ uri: team.team_logo }}
                style={styles.teamLogo}
                resizeMode="contain"
              />
            )}
            <Text style={styles.teamName} numberOfLines={1}>
              {team.team_name}
            </Text>
          </View>
          <Text style={styles.standingsCell}>{team.played}</Text>
          <Text style={[styles.standingsCell, { color: '#2e7d32' }]}>{team.won}</Text>
          <Text style={[styles.standingsCell, { color: '#ff9800' }]}>{team.drawn}</Text>
          <Text style={[styles.standingsCell, { color: '#d32f2f' }]}>{team.lost}</Text>
          <Text style={[styles.standingsCell, styles.pointsCell]}>{team.points}</Text>
        </View>
      ))}
    </View>
  );

  // Render content based on active tab
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
          <TouchableOpacity
            style={[styles.retryButton, { backgroundColor: currentColor }]}
            onPress={onRefresh}
          >
            <Text style={styles.retryButtonText}>إعادة المحاولة</Text>
          </TouchableOpacity>
        </View>
      );
    }

    if (activeTab === 'news') {
      if (news.length === 0) {
        return (
          <View style={styles.centerContainer}>
            <Ionicons name="newspaper-outline" size={48} color="#999" />
            <Text style={styles.emptyText}>لا توجد أخبار متاحة</Text>
          </View>
        );
      }
      return (
        <View style={styles.newsContainer}>
          {news.map(renderNewsItem)}
        </View>
      );
    }

    if (standings.length === 0) {
      return (
        <View style={styles.centerContainer}>
          <Ionicons name="trophy-outline" size={48} color="#999" />
          <Text style={styles.emptyText}>لا يوجد ترتيب متاح</Text>
        </View>
      );
    }
    return renderStandings();
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={currentColor} />
      
      {/* Header */}
      <View style={[styles.header, { backgroundColor: currentColor }]}>
        <Ionicons name="football-outline" size={28} color="#fff" />
        <Text style={styles.headerTitle}>أخبار الدوريات الأوروبية</Text>
        <Ionicons name="globe-outline" size={24} color="#fff" />
      </View>

      {/* League Selector */}
      {renderLeagueSelector()}

      {/* Tab Selector */}
      {renderTabSelector()}

      {/* Content */}
      <ScrollView
        style={styles.content}
        contentContainerStyle={styles.contentContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[currentColor]}
            tintColor={currentColor}
          />
        }
      >
        {renderContent()}
      </ScrollView>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>البيانات من يلا كورة</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  leagueSelector: {
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  leagueSelectorContent: {
    paddingHorizontal: 8,
    paddingVertical: 10,
  },
  leagueButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginHorizontal: 4,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: '#f9f9f9',
  },
  leagueButtonText: {
    fontSize: 13,
    color: '#333',
    fontWeight: '500',
  },
  leagueButtonTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    marginHorizontal: 4,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  tabText: {
    fontSize: 14,
    marginLeft: 6,
    color: '#666',
    fontWeight: '500',
  },
  tabTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 12,
    paddingBottom: 24,
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#666',
  },
  errorText: {
    marginTop: 12,
    fontSize: 14,
    color: '#d32f2f',
    textAlign: 'center',
  },
  emptyText: {
    marginTop: 12,
    fontSize: 14,
    color: '#999',
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 20,
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  newsContainer: {
    gap: 12,
  },
  newsCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    marginBottom: 12,
  },
  newsImage: {
    width: '100%',
    height: 180,
    backgroundColor: '#e0e0e0',
  },
  newsContent: {
    padding: 14,
  },
  newsTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#222',
    lineHeight: 24,
    textAlign: 'right',
  },
  newsDate: {
    marginTop: 8,
    fontSize: 12,
    color: '#888',
    textAlign: 'right',
  },
  standingsContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  standingsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  standingsHeader: {
    paddingVertical: 12,
  },
  headerText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  evenRow: {
    backgroundColor: '#fff',
  },
  oddRow: {
    backgroundColor: '#fafafa',
  },
  standingsCell: {
    flex: 1,
    fontSize: 12,
    textAlign: 'center',
    color: '#333',
  },
  teamCell: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  teamLogo: {
    width: 20,
    height: 20,
    marginLeft: 6,
  },
  teamName: {
    fontSize: 12,
    color: '#333',
    flex: 1,
    textAlign: 'right',
  },
  pointsCell: {
    fontWeight: 'bold',
    color: '#1a5f2a',
  },
  footer: {
    backgroundColor: '#fff',
    paddingVertical: 8,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  footerText: {
    fontSize: 11,
    color: '#999',
  },
});

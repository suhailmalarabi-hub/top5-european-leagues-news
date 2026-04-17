import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  Share,
  I18nManager,
  StatusBar,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useLocalSearchParams, useRouter } from 'expo-router';
import Constants from 'expo-constants';

I18nManager.allowRTL(true);
I18nManager.forceRTL(true);

const { width } = Dimensions.get('window');

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL ||
                process.env.EXPO_PUBLIC_BACKEND_URL ||
                'https://top5-league-app.preview.emergentagent.com';

const LEAGUE_COLORS: Record<string, string> = {
  'premier-league': '#3D195B',
  'la-liga': '#FF4B44',
  'serie-a': '#024494',
  'bundesliga': '#D20515',
  'ligue-1': '#091C3E',
};

const LEAGUE_NAMES: Record<string, string> = {
  'premier-league': 'الدوري الإنجليزي',
  'la-liga': 'الدوري الإسباني',
  'serie-a': 'الدوري الإيطالي',
  'bundesliga': 'الدوري الألماني',
  'ligue-1': 'الدوري الفرنسي',
};

export default function NewsDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{
    id: string;
    title: string;
    image_url: string;
    link: string;
    league_id: string;
    date: string;
  }>();

  const [content, setContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const color = LEAGUE_COLORS[params.league_id || ''] || '#3D195B';
  const leagueName = LEAGUE_NAMES[params.league_id || ''] || '';

  useEffect(() => {
    fetchDetail();
  }, []);

  const fetchDetail = async () => {
    try {
      const res = await fetch(`${API_URL}/api/news-detail/${params.league_id}/${params.id}`);
      if (res.ok) {
        const data = await res.json();
        setContent(data.content || null);
      }
    } catch {
      // Content optional
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    try {
      await Share.share({ message: `${params.title}`, title: params.title });
    } catch {}
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={color} />

      {/* Header */}
      <View style={[styles.header, { backgroundColor: color }]}>
        <TouchableOpacity testID="back-btn" onPress={() => router.back()} style={styles.headerBtn}>
          <Ionicons name="arrow-forward" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>{leagueName}</Text>
        <TouchableOpacity testID="share-btn" onPress={handleShare} style={styles.headerBtn}>
          <Ionicons name="share-social-outline" size={22} color="#fff" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.contentContainer}>
        {/* Hero Image */}
        {params.image_url ? (
          <Image source={{ uri: params.image_url }} style={styles.heroImage} resizeMode="cover" />
        ) : (
          <View style={[styles.heroPlaceholder, { backgroundColor: color + '15' }]}>
            <Ionicons name="newspaper-outline" size={60} color={color} />
          </View>
        )}

        {/* League Badge + Date */}
        <View style={styles.articleMeta}>
          <View style={[styles.leagueBadge, { backgroundColor: color }]}>
            <Text style={styles.leagueBadgeText}>{leagueName}</Text>
          </View>
          {params.date ? <Text style={styles.dateText}>{params.date}</Text> : null}
        </View>

        {/* Title */}
        <Text testID="article-title" style={styles.title}>{params.title}</Text>

        {/* Divider */}
        <View style={[styles.divider, { backgroundColor: color }]} />

        {/* Content */}
        {loading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator size="small" color={color} />
            <Text style={styles.loadingText}>جاري تحميل المقال...</Text>
          </View>
        ) : content ? (
          <View style={styles.articleBodyWrap}>
            {content.split('\n').filter(Boolean).map((paragraph, idx) => (
              <Text key={idx} style={styles.articleParagraph}>{paragraph}</Text>
            ))}
          </View>
        ) : (
          <View style={styles.noContentWrap}>
            <Ionicons name="document-text-outline" size={40} color="#ccc" />
            <Text style={styles.noContentText}>لا يتوفر نص المقال حالياً</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f2f2f7' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 8, paddingVertical: 10 },
  headerBtn: { padding: 8 },
  headerTitle: { fontSize: 16, fontWeight: 'bold', color: '#fff', flex: 1, textAlign: 'center' },
  scrollView: { flex: 1 },
  contentContainer: { paddingBottom: 40 },
  heroImage: { width: '100%', height: 240, backgroundColor: '#e5e5ea' },
  heroPlaceholder: { width: '100%', height: 180, alignItems: 'center', justifyContent: 'center' },
  articleMeta: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingTop: 14 },
  leagueBadge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  leagueBadgeText: { color: '#fff', fontSize: 11, fontWeight: 'bold' },
  dateText: { fontSize: 12, color: '#8e8e93' },
  title: { fontSize: 22, fontWeight: '800', color: '#1c1c1e', lineHeight: 34, paddingHorizontal: 16, paddingTop: 12, textAlign: 'right' },
  divider: { height: 3, width: 60, borderRadius: 2, marginHorizontal: 16, marginTop: 14, marginBottom: 16 },
  loadingWrap: { alignItems: 'center', paddingVertical: 30 },
  loadingText: { marginTop: 8, color: '#999', fontSize: 13 },
  articleBodyWrap: { paddingHorizontal: 16, gap: 14 },
  articleParagraph: { fontSize: 16, lineHeight: 30, color: '#333', textAlign: 'right' },
  noContentWrap: { alignItems: 'center', paddingVertical: 30, paddingHorizontal: 30 },
  noContentText: { marginTop: 10, color: '#999', fontSize: 14, textAlign: 'center', lineHeight: 22 },
});

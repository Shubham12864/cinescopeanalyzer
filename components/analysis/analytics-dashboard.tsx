"use client";

import { useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  PieChart, Pie, Cell, LineChart, Line, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, Star, Users, Clock, Award, 
  Calendar, Film, BarChart3, PieChart as PieChartIcon 
} from 'lucide-react';

interface AnalyticsDashboardProps {
  movieData: any;
  analyticsData: any;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

export default function AnalyticsDashboard({ movieData, analyticsData }: AnalyticsDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');

  // Process data for charts
  const genreData = movieData?.genre?.map((genre: string, index: number) => ({
    name: genre,
    value: Math.floor(Math.random() * 100) + 20, // Simulated popularity
    color: COLORS[index % COLORS.length]
  })) || [];

  const ratingDistribution = [
    { rating: '1-2', count: analyticsData?.rating_distribution?.low || 5 },
    { rating: '3-4', count: analyticsData?.rating_distribution?.medium_low || 15 },
    { rating: '5-6', count: analyticsData?.rating_distribution?.medium || 30 },
    { rating: '7-8', count: analyticsData?.rating_distribution?.high || 35 },
    { rating: '9-10', count: analyticsData?.rating_distribution?.very_high || 15 },
  ];

  const sentimentData = [
    { name: 'Positive', value: analyticsData?.sentiment_analysis?.positive || 65, color: '#00C49F' },
    { name: 'Neutral', value: analyticsData?.sentiment_analysis?.neutral || 25, color: '#FFBB28' },
    { name: 'Negative', value: analyticsData?.sentiment_analysis?.negative || 10, color: '#FF8042' },
  ];

  const timelineData = analyticsData?.timeline_data || [
    { month: 'Jan', reviews: 120, rating: 7.5 },
    { month: 'Feb', reviews: 150, rating: 7.8 },
    { month: 'Mar', reviews: 200, rating: 8.0 },
    { month: 'Apr', reviews: 180, rating: 8.2 },
    { month: 'May', reviews: 220, rating: 8.1 },
    { month: 'Jun', reviews: 250, rating: 8.3 },
  ];

  const performanceMetrics = {
    overall_score: analyticsData?.overall_score || movieData?.rating || 8.1,
    popularity_score: analyticsData?.popularity_score || 85,
    critical_reception: analyticsData?.critical_reception || 78,
    audience_score: analyticsData?.audience_score || 82,
    rewatchability: analyticsData?.rewatchability || 75,
    cultural_impact: analyticsData?.cultural_impact || 70,
  };

  const radarData = [
    { subject: 'Story', A: performanceMetrics.overall_score * 10, fullMark: 100 },
    { subject: 'Acting', A: (performanceMetrics.critical_reception / 10) * 10, fullMark: 100 },
    { subject: 'Direction', A: (performanceMetrics.popularity_score / 10) * 10, fullMark: 100 },
    { subject: 'Cinematography', A: 75, fullMark: 100 },
    { subject: 'Music', A: 80, fullMark: 100 },
    { subject: 'Effects', A: 70, fullMark: 100 },
  ];

  return (
    <div className="w-full space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Movie Analytics</h2>
          <p className="text-muted-foreground">
            Comprehensive analysis of {movieData?.title}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="secondary">
            <Star className="w-4 h-4 mr-1" />
            {movieData?.rating}/10
          </Badge>
          <Badge variant="outline">
            <Calendar className="w-4 h-4 mr-1" />
            {movieData?.year}
          </Badge>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="ratings">Ratings</TabsTrigger>
          <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Overall Rating</CardTitle>
                <Star className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{performanceMetrics.overall_score}/10</div>
                <p className="text-xs text-muted-foreground">Based on user reviews</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Popularity</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{performanceMetrics.popularity_score}%</div>
                <p className="text-xs text-muted-foreground">Trending score</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Reviews</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData?.total_reviews || movieData?.reviews?.length || 1247}</div>
                <p className="text-xs text-muted-foreground">Community feedback</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Runtime</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{movieData?.runtime || 120}m</div>
                <p className="text-xs text-muted-foreground">Duration</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Genre Distribution</CardTitle>
                <CardDescription>Popularity by genre</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={genreData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {genreData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Performance Radar</CardTitle>
                <CardDescription>Multi-dimensional analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis />
                    <Radar
                      name="Score"
                      dataKey="A"
                      stroke="#8884d8"
                      fill="#8884d8"
                      fillOpacity={0.6}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="ratings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Rating Distribution</CardTitle>
              <CardDescription>How users rated this movie</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={ratingDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="rating" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sentiment" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sentiment Analysis</CardTitle>
              <CardDescription>Overall sentiment from reviews</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Timeline Analysis</CardTitle>
              <CardDescription>Reviews and ratings over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Bar yAxisId="left" dataKey="reviews" fill="#8884d8" />
                  <Line yAxisId="right" type="monotone" dataKey="rating" stroke="#82ca9d" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

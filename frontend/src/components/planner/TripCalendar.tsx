import React, { useMemo, useState } from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { travelApi, API_BASE_URL } from '../../api/travel';
import { motion } from 'framer-motion';
import { CalendarDays } from 'lucide-react';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface TripCalendarProps {
  destination: string;
  duration: number;
  startDate: string;
  finalAnswer: string;
}

interface ParsedEvent {
  day: number;
  title: string;
  time: string;
  description: string;
}

interface TripCalendarEvent {
  title: string;
  start: Date;
  end: Date;
  allDay?: boolean;
}

const parseEvents = (text: string): ParsedEvent[] => {
  const dayPattern = /Day\s+(\d+):([\s\S]*?)(?=Day\s+\d+:|$)/gi;
  const events: ParsedEvent[] = [];
  let match;

  while ((match = dayPattern.exec(text)) !== null) {
    const day = parseInt(match[1], 10);
    const content = match[2];
    const lines = content.split('\n').filter(line => line.trim());

    lines.forEach(line => {
      const clean = line.replace(/^[-•*]\s*/, '').trim();
      if (!clean) return;
      events.push({
        day,
        title: clean.split('.')[0] || clean,
        time: '09:00',
        description: clean,
      });
    });
  }

  return events.slice(0, 20);
};

export const TripCalendar: React.FC<TripCalendarProps> = ({ destination, duration, startDate, finalAnswer }) => {
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [downloading, setDownloading] = useState(false);

  const start = useMemo(() => new Date(startDate), [startDate]);
  const end = useMemo(() => {
    const date = new Date(startDate);
    date.setDate(date.getDate() + Math.max(duration - 1, 0));
    return date;
  }, [startDate, duration]);

  const parsedEvents = useMemo(() => parseEvents(finalAnswer), [finalAnswer]);

  const calendarEvents: TripCalendarEvent[] = useMemo(() => {
    const tripBlock = {
      title: `Trip to ${destination}`,
      start,
      end: new Date(end.getTime() + 24 * 60 * 60 * 1000),
      allDay: true,
    } as TripCalendarEvent;

    const dayEvents = parsedEvents.map(event => {
      const eventDate = new Date(start);
      eventDate.setDate(eventDate.getDate() + event.day - 1);
      return {
        title: event.title,
        start: eventDate,
        end: eventDate,
        allDay: true,
      } as TripCalendarEvent;
    });

    return [tripBlock, ...dayEvents];
  }, [destination, start, end, parsedEvents]);

  const eventsByDay = useMemo(() => {
    return parsedEvents.reduce<Record<number, ParsedEvent[]>>((acc, event) => {
      if (!acc[event.day]) acc[event.day] = [];
      acc[event.day].push(event);
      return acc;
    }, {});
  }, [parsedEvents]);

  const handleExport = async () => {
    try {
      setDownloading(true);
      const payload = {
        destination,
        start_date: start.toISOString().slice(0, 10),
        end_date: end.toISOString().slice(0, 10),
        events: parsedEvents.map(event => ({
          day: event.day,
          title: event.title,
          time: event.time,
          description: event.description,
        })),
      };
      const response = await travelApi.exportCalendar(payload);
      window.open(`${API_BASE_URL}${response.download_url}`, '_blank');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="bg-gradient-to-b from-zinc-900/80 to-zinc-900/60 border border-zinc-800 rounded-2xl p-6 space-y-5 shadow-[0_10px_40px_rgba(0,0,0,0.35)]">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-violet-500/20 text-violet-300">
              <CalendarDays size={16} />
            </span>
            <h3 className="text-xl font-bold text-zinc-50">Trip Calendar</h3>
          </div>
          <p className="text-sm text-zinc-400 mt-1">Visualize your trip schedule</p>
        </div>
        <button
          onClick={handleExport}
          disabled={downloading}
          className="px-4 py-2 bg-orange-500 text-white rounded-xl text-sm font-semibold hover:bg-orange-400 transition disabled:opacity-60"
        >
          {downloading ? 'Generating...' : '📅 Add to Calendar'}
        </button>
      </div>

      <div className="musafir-calendar rounded-2xl border border-zinc-700/70 bg-zinc-950/40 p-3">
        <Calendar
          localizer={localizer}
          events={calendarEvents}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 390 }}
          views={['month']}
          onSelectEvent={(event: TripCalendarEvent) => {
            if (event.title.startsWith('Trip')) {
              setSelectedDay(null);
            } else {
              const dayIndex = parsedEvents.find(e => e.title === event.title)?.day || null;
              setSelectedDay(dayIndex);
            }
          }}
          eventPropGetter={(event: TripCalendarEvent) => {
            if (event.title.startsWith('Trip')) {
              return {
                style: {
                  backgroundColor: '#f97316',
                  border: 0,
                  borderRadius: '8px',
                  color: '#fff',
                  fontWeight: 700,
                  padding: '2px 8px',
                },
              };
            }
            return {
              style: {
                backgroundColor: '#7c3aed',
                border: 0,
                borderRadius: '8px',
                color: '#fff',
                fontWeight: 600,
                padding: '2px 8px',
              },
            };
          }}
        />
      </div>

      {selectedDay && eventsByDay[selectedDay] && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-zinc-800/60 border border-zinc-700 rounded-xl p-4"
        >
          <h4 className="text-sm font-semibold text-zinc-200 mb-3">
            <span className="inline-flex items-center rounded-full bg-violet-500/20 text-violet-200 px-2.5 py-1 mr-2">
              Day {selectedDay}
            </span>
            Itinerary
          </h4>
          <div className="space-y-2">
            {eventsByDay[selectedDay].map((event, index) => (
              <div key={index} className="text-sm text-zinc-300">
                <span className="text-orange-400 font-semibold">• </span>
                {event.description}
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};


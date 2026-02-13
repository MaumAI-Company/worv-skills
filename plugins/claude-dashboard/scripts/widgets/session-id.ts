/**
 * Session ID widget - displays the full session ID
 */

import type { Widget } from './base.js';
import type { WidgetContext, SessionIdData } from '../types.js';
import { COLORS, colorize } from '../utils/colors.js';

export const sessionIdWidget: Widget<SessionIdData> = {
  id: 'sessionId',
  name: 'Session ID',

  async getData(ctx: WidgetContext): Promise<SessionIdData | null> {
    const sessionId = ctx.stdin.session_id;
    if (!sessionId) {
      return null;
    }
    return { sessionId };
  },

  render(data: SessionIdData, _ctx: WidgetContext): string {
    // Display the full session ID
    return colorize(`🆔 ${data.sessionId}`, COLORS.dim);
  },
};
